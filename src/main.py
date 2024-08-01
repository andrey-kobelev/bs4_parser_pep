from collections import defaultdict
import logging
import re
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from constants import (
    BASE_DIR,
    WHATS_NEW_URL,
    LINK_TITLE_AUTHOR_HEAD,
    MAIN_DOC_URL,
    LINK_VERSION_STATUS_HEAD,
    VERSION_STATUS_PATTERN,
    DOWNLOADS_URL,
    MAIN_PEP_URL,
    EXPECTED_STATUS,
    STATUS_NUMBERS_HEAD,
    TOTAL_NUMBERS_HEAD,
    DOWNLOADS_DOCKS_DIR_NAME
)
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag, get_soup
from exceptions import ParserFindTagException


DOWNLOADS_SUCCESS_LOG = (
    'Архив был загружен и сохранён: {archive_path}'
)
MISMATCHED_STATUSES_LOG = 'НЕСОВПАДЕНИЕ СТАТУСОВ! {data}'
START_PARSER_LOG = 'Парсер запущен!'
COMMANDLINE_ARGS_LOG = 'Аргументы командной строки: {args}'
FINISH_PARSER_LOG = 'Парсер завершил работу.'
GENERAL_ERROR_LOG = (
    'Произошла ошибка во время работы парсера. '
    'Подробности: {error}'
)
EMPTY_TYPE_STATUS_COLUMN_LOG = (
    'PEP без типа и статуса: {peps}'
)
BAD_LINKS_LOG = '{}'

FIND_TAG_EXCEPTION = 'Ничего не нашлось'

MISMATCHED_STATUSES = (
    'Статус из списка: {status_from_pep_list}; '
    'Статус на странице {link}: {status_from_pep_page}'
)
BAD_LINK = 'Сбой при попытке пройти по ссылке: {link}'


def whats_new(session):
    results = [LINK_TITLE_AUTHOR_HEAD]
    bad_links = []
    for a_tag in tqdm(
        get_soup(session, WHATS_NEW_URL).select(
            '#what-s-new-in-python '
            'div.toctree-wrapper li.toctree-l1 > a'
        )
    ):
        href = a_tag['href']
        if not re.match(r'\d\.\d{,2}\.html', href):
            continue
        version_link = urljoin(WHATS_NEW_URL, href)
        try:
            soup = get_soup(session, version_link)
        except ConnectionError:
            bad_links.append(
                BAD_LINK.format(
                    link=version_link
                )
            )
            continue
        results.append(
            (
                version_link,
                find_tag(soup, 'h1').text,
                find_tag(soup, 'dl').text.replace('\n', ' ')
            )
        )
    if bad_links:
        logging.info(BAD_LINKS_LOG.format(*bad_links))
    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebar'})
    ul_tags = sidebar.find_all(name='ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindTagException(
            FIND_TAG_EXCEPTION
        )
    results = [LINK_VERSION_STATUS_HEAD]
    for a in a_tags:
        link = a['href']
        get_info = re.search(VERSION_STATUS_PATTERN, a.text)
        if get_info:
            version, status = get_info.groups()
        else:
            version, status = a.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    link_to_pdf = urljoin(
        DOWNLOADS_URL,
        get_soup(session, DOWNLOADS_URL).select_one(
            'table.docutils '
            'a[href$="pdf-a4.zip"]'
        )['href']
    )
    filename = link_to_pdf.split('/')[-1]
    # DOWNLOADS_DIR.mkdir(exist_ok=True)
    downloads_dir = BASE_DIR / DOWNLOADS_DOCKS_DIR_NAME
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    with open(archive_path, 'wb') as file:
        file.write(get_response(session, link_to_pdf).content)

    logging.info(
        DOWNLOADS_SUCCESS_LOG.format(
            archive_path=archive_path
        )
    )


def pep(session):
    soup = get_soup(session, MAIN_PEP_URL)
    pep_tables = (
        find_tag(
            soup=soup,
            tag='section',
            attrs={'id': 'pep-content'}
        )
    ).find_all(
        name='table',
        attrs={
            'class': 'pep-zero-table docutils align-default'
        }
    )
    statuses_nums = defaultdict(int)
    mismatched_statuses = []
    empty_type_and_status_columns = []
    for table in tqdm(pep_tables):
        for row in find_tag(soup=table, tag='tbody').find_all('tr'):
            link = urljoin(
                MAIN_PEP_URL,
                find_tag(
                    soup=row,
                    tag='a',
                    attrs={'href': re.compile(r'pep-\d{4}/$')}
                )['href']
            )
            status_from_pep_list = ''
            try:
                type_status = find_tag(soup=row, tag='abbr').text
                if len(type_status) == 2:
                    status_from_pep_list = type_status[1]
            except ParserFindTagException:
                empty_type_and_status_columns.append(link)
            pep_page_soup = get_soup(
                session, link
            )
            status_from_pep_page = find_tag(
                soup=pep_page_soup,
                tag='dl',
                attrs={'class': 'rfc2822 field-list simple'}
            ).find(
                string='Status'
            ).find_next('abbr').text
            if (
                status_from_pep_page
                in EXPECTED_STATUS[status_from_pep_list]
            ):
                statuses_nums[status_from_pep_page] += 1
            else:
                mismatched_statuses.append(
                    MISMATCHED_STATUSES.format(
                        status_from_pep_list=status_from_pep_list,
                        status_from_pep_page=status_from_pep_page,
                        link=link
                    )
                )
    if mismatched_statuses:
        logging.info(
            MISMATCHED_STATUSES_LOG.format(
                data=mismatched_statuses
            )
        )
    if empty_type_and_status_columns:
        logging.info(
            EMPTY_TYPE_STATUS_COLUMN_LOG.format(
                peps=empty_type_and_status_columns
            )
        )
    return [
        STATUS_NUMBERS_HEAD,
        *statuses_nums.items(),
        (TOTAL_NUMBERS_HEAD, sum(statuses_nums.values()))
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    try:
        configure_logging()
        logging.info(START_PARSER_LOG)
        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()

        logging.info(
            COMMANDLINE_ARGS_LOG.format(
                args=args
            )
        )

        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()

        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)

        if results is not None:
            control_output(results, args)

        logging.info(
            FINISH_PARSER_LOG
        )
    except Exception as error:
        logging.exception(
            GENERAL_ERROR_LOG.format(
                error=error
            ),
        )


if __name__ == '__main__':
    main()
