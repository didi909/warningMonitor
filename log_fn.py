import logging
import sys
import os

class Logger:
    def __init__(self, logName, logFile):
        self._logger = logging.getLogger(logName)
        self.handler = logging.FileHandler(logFile)
        formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        self.handler.setFormatter(formatter)
        self._logger.addHandler(self.handler)
        self._logger.setLevel(logging.INFO)

    def info(self, msg):
        if self._logger is not None:
            self._logger.info(msg)
    def error(self, msg):
        if self._logger is not None:
            self._logger.error(msg)
    def close(self):
        self._logger.removeHandler(self.handler)

