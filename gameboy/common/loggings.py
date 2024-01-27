import logging
import os
from typing import Optional

pkg_path = os.path.abspath(os.path.join(__file__, '..', '..'))


class LoggerFactory:

    def __init__(self):
        log_format = '%(asctime)s - %(name)s - [%(levelname)s] %(message)s'
        # log_format = '%(name)s - [%(levelname)s] %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter(log_format, date_format)

        self.log_level = logging.WARNING
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(logging.DEBUG)
        self.stream_handler.setFormatter(formatter)
        self.file_handler = logging.FileHandler(
            filename='gameboy.log', mode='w',
        )
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(formatter)

    def get_logger(
        self,
        name: Optional[str] = None,
        file: Optional[str] = None,
    ) -> logging.Logger:
        file = os.path.relpath(file, pkg_path) if file is not None else None
        logger_name = name or file or ''
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.log_level)
        logger.addHandler(self.stream_handler)
        logger.addHandler(self.file_handler)

        return logger


logger_factory = LoggerFactory()


def get_logger(
    name: Optional[str] = None, file: Optional[str] = None,
) -> logging.Logger:
    return logger_factory.get_logger(name=name, file=file)


__all__ = ['get_logger']
