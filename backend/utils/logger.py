import logging
import os
from logging.handlers import RotatingFileHandler

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'


def configure_logging():
    logger = logging.getLogger('backend')
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, 'app.log'), maxBytes=10_485_760, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    error_logger = logging.getLogger('backend.error')
    if not error_logger.handlers:
        error_logger.setLevel(logging.ERROR)
        error_logger.addHandler(console_handler)
        error_logger.addHandler(file_handler)

    return logger
