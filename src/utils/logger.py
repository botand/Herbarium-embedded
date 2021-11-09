"""Logger helpers"""
import sys
from logging import getLogger, handlers, StreamHandler, Formatter, debug
from src.utils import config

_FORMATTER = Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
_DEFAULT_LEVEL = config["logging"]["level"]


def _get_console_handler():
    """
    :return: a stream handler to display logs in the console
    """
    console_handler = StreamHandler(sys.stdout)
    console_handler.setFormatter(_FORMATTER)
    return console_handler


def _get_file_handler():
    """
    :return: a file handler to save logs in a file
    """
    file_handler = handlers.TimedRotatingFileHandler(
        f"{config['logging']['path']}/{config['version']}{config['logging']['filename_suffix']}",
        when="midnight",
        interval=1,
    )
    file_handler.setFormatter(_FORMATTER)
    return file_handler


def get_logger(logger_name, logger_level=_DEFAULT_LEVEL):
    """
    Create a new logger.
    :param logger_name: name of the logger
    :type logger_name str
    :param logger_level
    :return: logger
    """
    logger = getLogger(logger_name)
    logger.setLevel(logger_level)
    logger.addHandler(_get_console_handler())
    logger.addHandler(_get_file_handler())
    logger.propagate = False

    debug("Adding logger: %s", logger_name)
    return logger
