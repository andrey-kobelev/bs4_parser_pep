from pathlib import Path
from urllib.parse import urljoin

MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'
WHATS_NEW_URL = urljoin(
    MAIN_DOC_URL, 'whatsnew/'
)
DOWNLOADS_URL = urljoin(
    MAIN_DOC_URL, 'download.html'
)

RESULTS_FILES_DIR_NAME = 'results'
DOWNLOADS_DOCKS_DIR_NAME = 'downloads'

BASE_DIR = Path(__file__).parent
RESULTS_FILES_DIR = BASE_DIR / RESULTS_FILES_DIR_NAME
DOWNLOADS_DOCKS_DIR = BASE_DIR / DOWNLOADS_DOCKS_DIR_NAME

CSV_FILE_NAME = '{parser_mode}_{datetime_now}.csv'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

LINK_VERSION_STATUS_HEAD = ('Ссылка на документацию', 'Версия', 'Статус')
STATUS_NUMBERS_HEAD = ('Статус', 'Количество')
TOTAL_NUMBERS_HEAD = 'Общее количество'
LINK_TITLE_AUTHOR_HEAD = ('Ссылка на статью', 'Заголовок', 'Редактор, автор')

VERSION_STATUS_PATTERN = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

# Argparse constants.
PRETTY_OUTPUT = 'pretty'
FILE_OUTPUT = 'file'

MODE_ARGUMENT_HELP = 'Режимы работы парсера'
CLEAR_CACHE_ARGUMENT_HELP = 'Очистка кеша'
OUTPUT_ARGUMENT_HELP = 'Дополнительные способы вывода данных'
ARGPARSE_DESCRIPTION = 'Парсер документации Python'

# Logger constants.
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'

LOG_DIR_NAME = 'logs'
LOG_FILE_NAME = 'parser.log'

LOG_DIR = BASE_DIR / LOG_DIR_NAME
LOG_FILE = LOG_DIR / LOG_FILE_NAME
