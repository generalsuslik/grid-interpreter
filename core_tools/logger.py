import logging
from copy import copy


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
    logger.propagate = False
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = CustomUnixFormatter(
        "[%(name)s][%(levelname)s]  %(message)s (%(filename)s:%(lineno)d)"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
