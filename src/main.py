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
    PDF_FILE_PATTERN,
    MAIN_PEP_URL,
    EXPECTED_STATUS,
    STATUS_NUMBERS_HEAD,
    TOTAL_NUMBERS_HEAD,
    WHATS_NEW_MODE,
    LATEST_VERSIONS_MODE,
    DOWNLOAD_MODE,
    PEP_MODE
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
BAD_LINKS_LOG = 'Сбой при попытке пройти по ссылкам(ке): {links}'

FIND_TAG_EXCEPTION = 'Ничего не нашлось'

MISMATCHED_STATUSES = (
    'Статус из списка: {status_from_pep_list}; '
    'Статус на странице {link}: {status_from_pep_page}'
)


def whats_new(session):
    response = get_response(session, WHATS_NEW_URL)
    if response is None:
        return
    soup = get_soup(response)
    main_div = find_tag(
        soup, 'section', {'id': 'what-s-new-in-python'}
    )
    div_with_ul = find_tag(
        main_div, 'div', {'class': 'toctree-wrapper'}
    )
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [LINK_TITLE_AUTHOR_HEAD]
    bad_links = []
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(WHATS_NEW_URL, href)
        response = get_response(session, version_link)
        if response is None:
            bad_links.append(version_link)
            continue
        soup = get_soup(response)
        h1 = find_tag(soup, 'h1').text
        dl = find_tag(soup, 'dl').text.replace('\n', ' ')
        results.append(
            (version_link, h1, dl)
        )
    if bad_links:
        logging.info(BAD_LINKS_LOG.format(links=bad_links))
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = get_soup(response)
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
    response = get_response(session, DOWNLOADS_URL)
    if response is None:
        return
    soup = get_soup(response)
    table = find_tag(soup, 'table', {'class': 'docutils'})
    a_tags = find_tag(
        table,
        'a',
        {'href': re.compile(PDF_FILE_PATTERN)}
    )
    link_to_pdf = urljoin(DOWNLOADS_URL, a_tags['href'])

    filename = link_to_pdf.split('/')[-1]
    # DOWNLOADS_DIR.mkdir(exist_ok=True)
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = get_response(session, link_to_pdf)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(
        DOWNLOADS_SUCCESS_LOG.format(
            archive_path=archive_path
        )
    )


def pep(session):
    response = get_response(session, MAIN_PEP_URL)
    soup = get_soup(response)
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
    status_num = defaultdict(int)
    mismatched_statuses = []
    for table in tqdm(pep_tables):
        for row in find_tag(soup=table, tag='tbody').find_all('tr'):
            try:
                type_status = find_tag(soup=row, tag='abbr')
            except ParserFindTagException:
                type_status = None
            status_from_pep_list = ''
            if type_status:
                type_status = type_status.text
                if len(type_status) == 2:
                    status_from_pep_list = type_status[1]
            link = urljoin(
                MAIN_PEP_URL,
                find_tag(
                    soup=row,
                    tag='a',
                    attrs={'href': re.compile(r'pep-\d{4}/$')}
                )['href']
            )
            pep_page_soup = get_soup(
                get_response(session, link)
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
                status_num[status_from_pep_page] += 1
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
    return [
        STATUS_NUMBERS_HEAD,
        *status_num.items(),
        (TOTAL_NUMBERS_HEAD, sum(status_num.values()))
    ]


MODE_TO_FUNCTION = {
    WHATS_NEW_MODE: whats_new,
    LATEST_VERSIONS_MODE: latest_versions,
    DOWNLOAD_MODE: download,
    PEP_MODE: pep
}


def main():
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


if __name__ == '__main__':
    main()
