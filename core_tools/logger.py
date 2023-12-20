import logging
import platform
from copy import copy


class CustomWindowsFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def __init__(self):
        logging.Formatter.__init__(self)

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class CustomUnixFormatter(logging.Formatter):
    FORMATS = {
        "DEBUG": 37,  # white
        "INFO": 36,  # cyan
        "WARNING": 33,  # yellow
        "ERROR": 31,  # red
        "CRITICAL": 41,  # white on red bg
    }

    PREFIX = "\033["
    SUFFIX = "\033[0m"

    def __init__(self, pattern):
        logging.Formatter.__init__(self, pattern)

    def format(self, record):
        colored_record = copy(record)
        levelname = colored_record.levelname
        seq = self.FORMATS.get(levelname, 37)  # default white
        colored_levelname = f"{self.PREFIX}{seq}m{levelname}{self.SUFFIX}"
        colored_record.levelname = colored_levelname
        return logging.Formatter.format(self, colored_record)


def setup_logger():
    logger = logging.getLogger("Main_logger")
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    if platform.system() != "Windows":
        formatter = CustomUnixFormatter(
            "[%(name)s][%(levelname)s]  %(message)s (%(filename)s:%(lineno)d)"
        )
    else:
        formatter = CustomWindowsFormatter()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
