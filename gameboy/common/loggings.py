import logging
import os

pkg_path = os.path.abspath(os.path.join(__file__, '..', '..'))


class LoggerFactory:

    log_time_prefix = '%(asctime)s - '
    log_format = '%(name)s - [%(levelname)s] %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    def __init__(self):
        formatter = self.get_formatter(display_time=True)
        log_level = logging.DEBUG

        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(formatter)
        self.stream_handler.setLevel(log_level)
        self.file_handler = logging.FileHandler('gameboy.log', mode='w')
        self.file_handler.setFormatter(formatter)
        self.file_handler.setLevel(log_level)

    def get_formatter(self, display_time: bool) -> logging.Formatter:
        fmt = self.log_format
        if display_time:
            fmt = self.log_time_prefix + fmt
        return logging.Formatter(fmt=fmt, datefmt=self.date_format)

    def get_logger(self, file: str) -> logging.Logger:
        logger_name = os.path.relpath(file, pkg_path)
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.file_handler)
        logger.addHandler(self.stream_handler)

        return logger

    def set_level(self, level: int):
        self.file_handler.setLevel(level=level)
        self.stream_handler.setLevel(level=level)

    def set_display_time(self, enable: bool):
        formatter = self.get_formatter(display_time=enable)
        self.file_handler.setFormatter(formatter)
        self.stream_handler.setFormatter(formatter)


logger_factory = LoggerFactory()


def get_logger(file: str):
    return logger_factory.get_logger(file=file)


def set_level(level: int):
    logger_factory.set_level(level=level)


def set_display_time(enable: bool):
    logger_factory.set_display_time(enable=enable)
