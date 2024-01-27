from faker import Faker
from typing import Dict, Optional, List, Any

NLP_CONFIGURATION = [
    {"lang_code": "en", "model_name": "en_core_web_md"},
    {"lang_code": "zh", "model_name": "zh_core_web_md"},
]


SUPPORTED_LANG_CODES = [item["lang_code"] for item in NLP_CONFIGURATION]

def load_base_entities_and_masking_function(seed: Optional[int] = None) -> List[Dict[str, Any]]:
    fake = Faker()
    fake.seed_instance(seed)
    return [
        {
            "entity": "PERSON",
            "masking_function": lambda _: fake.name(),
        },
        {
            "entity": "EMAIL_ADDRESS",
            "masking_function": lambda _: fake.email(),
        },
        {
            "entity": "CREDIT_CARD",
            "masking_function": lambda _: fake.credit_card_number(),
        },
        {
            "entity": "LOCATION",
            "masking_function": lambda _: lambda _: fake.city(),
        },
        {
            "entity": "PHONE_NUMBER",
            "masking_function": lambda _: fake.phone_number(),
        },
        {
            "entity": "SG_NRIC_FIN",
            "masking_function": lambda _: fake.bothify(text="????####?").upper(),
        }
    ]

def load_custom_regex_and_masking_function(seed: Optional[int] = None) -> List[Dict[str, Any]]:
    fake = Faker()
    fake.seed_instance(seed)
    return [ 
        {
            "name": "SINGAPORE_PHONE_NUMBER",
            "regex_list": ["(?<!\w)(\(?(\+|00)?65\)?)?[ -]?\d{4}[ -]?\d{4}(?!\w)"],
            "context_list": ["phone", "number"],
            "masking_function": lambda _: fake.phone_number(),
        }
    ]
