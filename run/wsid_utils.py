__author__ = 'thorn'
import logging
import sys

LOGGER = logging.getLogger()

def prepare_logger(log_level, filename=None):
    log_level = getattr(logging, log_level.upper(), None)

    if filename is None:
        filename = sys.stderr

    LOGGER.setLevel(level=log_level)
    handler = logging.StreamHandler(filename)
    handler.setLevel(log_level)
    formatter = logging.Formatter(
        u'[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
