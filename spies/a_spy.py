""" define common behavor """
import logging
from utils.trace import Trace


class ASpy():
    """ define common behavor """

    def __init__(self, spy_name: str = None):
        """ set spyer name
        """
        self.spy_name = spy_name
        self._logger = Trace.get_logger(self)

    def set_logger_level(self, log_level=logging.DEBUG):
        """
        Set logger level
        """
        self._logger.setLevel(log_level)

    def get_logger(self, log_level=logging.DEBUG):
        """
        Get logger
        """
        if log_level:
            self.set_logger_level(log_level)
        return self._logger
