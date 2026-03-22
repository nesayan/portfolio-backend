import logging

LOGGER_NAME = "app"

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)

# Console handler with formatter
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(console_handler)

