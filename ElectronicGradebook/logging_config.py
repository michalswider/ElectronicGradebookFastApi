import logging
from logging.handlers import RotatingFileHandler


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler('app.log', maxBytes=2000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
