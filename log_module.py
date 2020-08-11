import logging
import sys
# from logging.handlers import TimedRotatingFileHandler
from logging import FileHandler

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = "fun_with_api.log"


def get_console_handler():
    """
    This function creates the handler that prints directly to the system console
    :return: the console handler
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    """
    This function creates the handler that writes to a log file
    :return: the file handler
    """
    file_handler = FileHandler(LOG_FILE, mode='a', encoding=None, delay=False)
    # file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    """
    This function can be called from other modules to create a new logger object for them
    :param logger_name: usually, it should receive this argument as __name__, not as a hardcoded value
    :return: the logger object
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger
