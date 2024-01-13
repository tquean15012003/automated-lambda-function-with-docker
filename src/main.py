import logging

logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger(__name__)

def handler(event, context):
    logger.info(f"Received event\n{event}")
    logger.info(f"Received context\n{context}")

    return "Hello world"