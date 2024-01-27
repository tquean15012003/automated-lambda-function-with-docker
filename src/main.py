import logging

from model import AnonymizeResult, DeanonymizeResult
from helpers.PPIMaskingManager import PIIMaskingManager

logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger(__name__)


def handler(event, context):
    logger.info(f"Received event\n{event}")

    text = event.get("text", None)
    operation = event.get("operation", "anonymize")

    if text == None:
        raise ValueError("Missing 'text' in the request body")
    pii_masking_manager = PIIMaskingManager()
    try:
        if operation == "anonymize":
            (
                anonymized_text,
                deanonymizer_mapping,
            ) = pii_masking_manager.get_anonymized_text(text=text)

            return AnonymizeResult(
                data=anonymized_text,
                deanonymizer_mapping=deanonymizer_mapping,
                status="success",
            )
        elif operation == "deanonymize":
            deanonymizer_mapping = event.get("deanonymizer_mapping", None)
            if deanonymizer_mapping == None:
                raise ValueError("Missing 'deanonymizer_mapping' in the request body")

            anonymized_text = pii_masking_manager.get_deanonymized_text(
                text=text, deanonymizer_mapping=deanonymizer_mapping
            )
            return DeanonymizeResult(data=anonymized_text, status="success")
        else:
            raise ValueError("Invalid operation")
    except Exception as e:
        raise Exception(e)
