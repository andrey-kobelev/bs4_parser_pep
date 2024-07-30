import csv

import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (
    CSV_FILE_NAME,
    DATETIME_FORMAT,
    ENCODING,
    PRETTY_OUTPUT,
    FILE_OUTPUT,
    BASE_DIR
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


def file_output(results, **kwargs):
    # RESULTS_DIR.mkdir(exist_ok=True)
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    file_path = results_dir / CSV_FILE_NAME.format(
        parser_mode=kwargs['cli_args'].mode,
        datetime_now=dt.datetime.now().strftime(
            DATETIME_FORMAT
        )
    )
    with open(
        file_path, 'w', encoding=ENCODING
    ) as results_file:
        writer = csv.writer(
            results_file, dialect=csv.unix_dialect
        )
        writer.writerows(results)

    logging.info(SAVE_FILE_LOG.format(file_path=file_path))


def control_output(results, cli_args):
    output = cli_args.output
    outputs = {
        PRETTY_OUTPUT: pretty_output,
        FILE_OUTPUT: file_output,
        None: default_output
    }
    outputs[output](results, cli_args=cli_args)
