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

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / 'results'
DOWNLOADS_DIR = BASE_DIR / 'downloads'

CSV_FILE_NAME = '{parser_mode}_{datetime_now}.csv'

ENCODING = 'utf-8'

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
PDF_FILE_PATTERN = r'.+pdf-a4\.zip$'

# Argparse constants.
PRETTY_OUTPUT = 'pretty'
FILE_OUTPUT = 'file'

MODE_ARGUMENT_HELP = 'Режимы работы парсера'
CLEAR_CACHE_ARGUMENT_HELP = 'Очистка кеша'
OUTPUT_ARGUMENT_HELP = 'Дополнительные способы вывода данных'
ARGPARSE_DESCRIPTION = 'Парсер документации Python'

WHATS_NEW_MODE = 'whats-new'
LATEST_VERSIONS_MODE = 'latest-versions'
DOWNLOAD_MODE = 'download'
PEP_MODE = 'pep'

# Logger constants.
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'
