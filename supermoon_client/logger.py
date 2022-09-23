import logging
from logging.handlers import RotatingFileHandler

from supermoon_client.consts import LOG_FILE_NAME, LOGGER_NAME

logging.basicConfig(level=logging.DEBUG)

_logger = None


def _get_file_handler():
    file_handler = RotatingFileHandler(LOG_FILE_NAME)
    file_handler.setLevel(logging.DEBUG)
    return file_handler


def configure_root_logger():
    logging.getLogger().addHandler(_get_file_handler())


def get_logger():
    global _logger

    if not _logger:
        _logger = logging.getLogger(LOGGER_NAME)
        _logger.addHandler(_get_file_handler())

    return _logger
