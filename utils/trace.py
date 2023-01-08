"""Logger"""
import os
from pathlib import Path
from time import time
import logging
import logging.config
import yaml
import wrapt

class Trace:
    """Trace to debug"""
    _is_logger_config = None
    _loggers = {}
    INT_RUNTIME_ID = 0
    @staticmethod
    def _get_object_fullname(instance):
        class_ = instance.__class__
        str_module = class_.__module__
        if str_module == 'builtins':
            return class_.__qualname__
        return str_module + '.' + class_.__qualname__

    @staticmethod
    def get_logger(instance, str_logger_name=None, str_prefix:str=""):
        """
        Common logger
        """
        str_logger_name = Trace._get_object_fullname(instance) \
            if str_logger_name is None else str_logger_name
        if Trace._is_logger_config is None:
            str_dir_path = os.path.join(os.path.dirname(__file__))
            str_path = f"{str_dir_path}/config/trace.yml"
            with open(str_path, encoding='utf-8') as yaml_conf_file:
                Trace._is_logger_config = True
                logging.config.dictConfig(\
                    yaml.safe_load(yaml_conf_file))
        str_prefix = " - {}" if str_prefix else ""
        str_logger_name = f"[{Trace.INT_RUNTIME_ID}] - {str_logger_name} {str_prefix}"
        if str_logger_name not in Trace._loggers:
            Trace._loggers[str_logger_name] = \
            logging.getLogger(str_logger_name)
        return Trace._loggers[str_logger_name]

    def __init__(self, level=logging.DEBUG, logger_name=""):
        self.level = level
        self.logger_name = logger_name

    @wrapt.decorator
    def __call__(self, wrapped, instance, args, kwargs):
        str_logger_name = self.logger_name
        if not str_logger_name:
            class_name=Trace._get_object_fullname(instance)
            method_name=wrapped.__name__
            str_logger_name = f"{class_name}.{method_name}"
        logger = Trace.get_logger(None, str_logger_name)
        logger.setLevel(self.level)
        logger.debug(f"Start with *args[{args}], **kwargs[{kwargs}]")
        time_execution_start = time()
        result = wrapped(*args, **kwargs)
        time_execution_end = time()
        sec_elapsed = time_execution_end-time_execution_start
        logger.setLevel(self.level)
        logger.debug(f"return[{result}]")
        logger.debug(f"Execution took {sec_elapsed} seconds")
        return result
