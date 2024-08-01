import csv

import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (
    CSV_FILE_NAME,
    DATETIME_FORMAT,
    PRETTY_OUTPUT,
    FILE_OUTPUT,
    BASE_DIR,
    RESULTS_FILES_DIR_NAME
)

SAVE_FILE_LOG = (
    'Файл с результатами '
    'был сохранён: {file_path}'
)


def default_output(results, **kwargs):
    for row in results:
        print(*row)


def pretty_output(results, **kwargs):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, encode='utf-8', **kwargs):
    # RESULTS_DIR.mkdir(exist_ok=True)
    results_dir = BASE_DIR / RESULTS_FILES_DIR_NAME
    results_dir.mkdir(exist_ok=True)
    file_path = results_dir / CSV_FILE_NAME.format(
        parser_mode=kwargs['cli_args'].mode,
        datetime_now=dt.datetime.now().strftime(
            DATETIME_FORMAT
        )
    )
    with open(
        file_path, 'w', encoding=encode
    ) as results_file:
        csv.writer(
            results_file, dialect=csv.unix_dialect
        ).writerows(results)

    logging.info(SAVE_FILE_LOG.format(file_path=file_path))


OUTPUTS = {
        PRETTY_OUTPUT: pretty_output,
        FILE_OUTPUT: file_output,
        None: default_output
    }


def control_output(results, cli_args):
    OUTPUTS[cli_args.output](results, cli_args=cli_args)
