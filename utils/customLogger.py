import logging
import sys
from datetime import datetime


class CustomLogger:

    def __init__(self, logging_level=logging.DEBUG, console=False):
        self._name = 'Base'
        self._title = 'Base'
        self.FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
        self.LOG_FILE = "rcesm_diag"+datetime.now().strftime("%Y%m%d%H%M%S)")+".log"
        self.logger = self.get_logger('rcesm', console, logging_level)
        return self.logger

    def get_console_handler(self, logging_level):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.FORMATTER)
        console_handler.setLevel(level=logging_level)
        return console_handler

    def get_file_handler(self, logging_level):
        file_handler = logging.FileHandler(self.LOG_FILE)
        file_handler.setFormatter(self.FORMATTER)
        file_handler.setLevel(level=logging_level)
        return file_handler

    def get_logger(self, logger_name, console, logging_level):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
        logger.addHandler(self.get_console_handler(logging_level=logging_level))
        if console:
            logger.addHandler(self.get_file_handler(logging_level=logging_level))
        # with this pattern, it's rarely necessary to propagate the error up to parent
        logger.propagate = False
        return logger
