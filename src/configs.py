import argparse
import logging
from logging.handlers import RotatingFileHandler

import constants


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(
        description=constants.ARGPARSE_DESCRIPTION
    )
    parser.add_argument(
        'mode',
        choices=available_modes,
        help=constants.MODE_ARGUMENT_HELP
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help=constants.CLEAR_CACHE_ARGUMENT_HELP
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(constants.PRETTY_OUTPUT, constants.FILE_OUTPUT),
        help=constants.OUTPUT_ARGUMENT_HELP
    )
    return parser


def configure_logging():
    constants.LOG_DIR.mkdir(exist_ok=True)
    rotating_handler = RotatingFileHandler(
        constants.LOG_FILE, maxBytes=10 ** 6, backupCount=5
    )
    logging.basicConfig(
        datefmt=constants.DT_FORMAT,
        format=constants.LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
