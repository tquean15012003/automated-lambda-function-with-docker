import logging
from helpers.DeanonymizerMapping import MappingDataType, create_anonymizer_mapping
from helpers.DeanonymizerMatchingStrategy import exact_matching_strategy

from helpers.constants import (
    NLP_CONFIGURATION,
    SUPPORTED_LANG_CODES,
    load_base_entities_and_masking_function,
    load_custom_regex_and_masking_function,
)

from typing import Optional, Callable
from pydantic import BaseModel

from spacy import load
from spacy.language import Language
from spacy_fastlang import LanguageDetector  # Do not delete

from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer import (
    AnalyzerEngine,
    RecognizerRegistry,
    PatternRecognizer,
    Pattern,
)

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig, ConflictResolutionStrategy

logger = logging.getLogger(__name__)


class CustomRecognizer(BaseModel):
    """
    Example:
        - "name": "SINGAPORE_PHONE_NUMBER",
        - "regex_list": ["(?<!\w)(\(?(\+|00)?65\)?)?[ -]?\d{4}[ -]?\d{4}(?!\w)"],
        - "masking_function": lambda _: fake.phone_number(),
        - "context_list": ["phone", "number"]
    """

    name: str
    regex_list: list[str]
    masking_function: Callable
    context_list: Optional[list[str]] = None


class PIIMaskingManager:
    def __init__(
        self,
        faker_seed: Optional[int] = None,
    ) -> None:
        base_entities_and_masking_function = load_base_entities_and_masking_function(
            seed=faker_seed
        )

        self.supported_entities = [
            item["entity"] for item in base_entities_and_masking_function
        ]
        self.masking_operators = {
            item["entity"]: OperatorConfig(
                operator_name="custom", params={"lambda": item["masking_function"]}
            )
            for item in base_entities_and_masking_function
        }

        self.analyzer = self.__init_analyzer()
        self.anonymizer = AnonymizerEngine()

        self.__load_custom_regex(seed=faker_seed)

    @property
    def anonymizer_mapping(self) -> MappingDataType:
        """Return the anonymizer mapping
        This is just the reverse version of the deanonymizer mapping."""
        return {
            key: {v: k for k, v in inner_dict.items()}
            for key, inner_dict in self.deanonymizer_mapping.items()
        }

    def get_anonymized_text(self, text: str):
        lang_code = self.__detect_language(text)

        if lang_code not in SUPPORTED_LANG_CODES:
            message = "Language {lang_code} is not supported."
            logger.error(message)
            raise ValueError(message)

        # Perform initial anonymization
        anonymized_text = self.__anonymize_text(text=text, lang_code=lang_code)

        logger.info(f"Got anonymized text - {anonymized_text}")
        logger.info(f"Got deanonymized mapping - {self.deanonymizer_mapping}")

        return anonymized_text, dict(self.deanonymizer_mapping)

    def get_deanonymized_text(
        self, text: str, deanonymizer_mapping: MappingDataType
    ) -> str:
        deanonymized_text = exact_matching_strategy(text, deanonymizer_mapping)
        logger.info(f"Got deanonymized text: {deanonymized_text}")
        return deanonymized_text

    def __load_spacy_model(self) -> Language:
        nlp = load("en_core_web_md")
        nlp.add_pipe("language_detector")

        return nlp

    def __detect_language(self, text: str):
        nlp = self.__load_spacy_model()
        doc = nlp(text)
        lang_code = doc._.language
        logger.info(f"Language detected - {lang_code}")

        return lang_code

    def __analyze_text(self, text: str, lang_code: str):
        """
        Analyze text with the analyzer to recognize all entities and their location
        """
        results = self.analyzer.analyze(
            text=text, language=lang_code, entities=self.supported_entities
        )

        return results

    def __anonymize_text(
        self, text: str, lang_code: str
    ) -> tuple[str, MappingDataType]:
        # Analyze text
        analyzer_results = self.__analyze_text(text=text, lang_code=lang_code)

        # Remove conflicts caused by two entities identified at the same position
        filtered_analyzer_results = (
            self.anonymizer._remove_conflicts_and_get_text_manipulation_data(
                analyzer_results=analyzer_results,
                conflict_resolution=ConflictResolutionStrategy.REMOVE_INTERSECTIONS
            )
        )
        logger.info(f"Got analyzer results\n{filtered_analyzer_results}")

        # Anonymize text for the first time
        anonymized_results = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators=self.masking_operators,
        )
        
        self.deanonymizer_mapping = create_anonymizer_mapping(
            text, filtered_analyzer_results, anonymized_results, is_reversed=True
        )

        clean_anonymized_text = exact_matching_strategy(text, self.anonymizer_mapping)

        return clean_anonymized_text

    def __init_analyzer(self) -> AnalyzerEngine:
        """
        Initialize analyzer which is to identify the entities and their position in the text
        """

        # Create NLP engine based on configuration
        registry = RecognizerRegistry()
        provider = NlpEngineProvider(
            nlp_configuration={
                "nlp_engine_name": "spacy",
                "models": NLP_CONFIGURATION,
            }
        )
        nlp_engine = provider.create_engine()

        # Pass the created NLP engine and supported_languages to the AnalyzerEngine
        analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine,
            supported_languages=SUPPORTED_LANG_CODES,
            registry=registry,
        )

        return analyzer

    def __load_custom_regex(self, seed: Optional[int] = None):
        logger.info(f"Load custom regex")
        custom_regex_and_masking_function = load_custom_regex_and_masking_function(
            seed=seed
        )
        for item in custom_regex_and_masking_function:
            self.__create_custom_recognizer(
                data=CustomRecognizer(
                    name=item["name"],
                    regex_list=item["regex_list"],
                    context_list=item["context_list"],
                    masking_function=item["masking_function"],
                )
            )

    def __create_custom_recognizer(self, data: CustomRecognizer) -> None:
        """
        Used to add any custom regex identifier
        """
        if not self.analyzer:
            raise ValueError("Analyzer has not been initialized!")

        patterns = [
            Pattern(
                name=data.name,
                regex=regex,
                score=1,
            )
            for regex in data.regex_list
        ]
        recognizers = [
            PatternRecognizer(
                supported_entity=data.name,
                patterns=patterns,
                context=data.context_list,
                supported_language=lang_code,
            )
            for lang_code in SUPPORTED_LANG_CODES
        ]
        self.supported_entities.append(data.name)

        self.masking_operators.update(
            {
                data.name: OperatorConfig(
                    operator_name="custom", params={"lambda": data.masking_function}
                )
            }
        )

        for recognizer in recognizers:
            self.analyzer.registry.add_recognizer(recognizer)
