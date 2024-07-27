import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from constants import BASE_DIR, MAIN_DOC_URL, MAIN_PEP_URL, EXPECTED_STATUS
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag
from exceptions import ParserFindTagException


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(
        soup, 'section', {'id': 'what-s-new-in-python'}
    )
    div_with_ul = find_tag(
        main_div, 'div', {'class': 'toctree-wrapper'}
    )
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1').text
        dl = find_tag(soup, 'dl').text.replace('\n', ' ')
        results.append(
            (version_link, h1, dl)
        )
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebar'})
    ul_tags = sidebar.find_all(name='ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for a in a_tags:
        link = a['href']
        get_info = re.search(pattern, a.text)
        if get_info:
            version, status = get_info.groups()
        else:
            version, status = a.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    table = find_tag(soup, 'table', {'class': 'docutils'})
    pattern = r'.+pdf-a4\.zip$'
    a_tags = find_tag(table, 'a', {'href': re.compile(pattern)})
    link_to_pdf = urljoin(downloads_url, a_tags['href'])

    filename = link_to_pdf.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(link_to_pdf)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, MAIN_PEP_URL)
    soup = BeautifulSoup(response.text, features='lxml')
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
    total = 0
    status_num = dict()
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
            pep_page_soup = BeautifulSoup(
                session.get(link).text, features='lxml'
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
                if status_from_pep_page not in status_num:
                    status_num[status_from_pep_page] = 1
                else:
                    status_num[status_from_pep_page] += 1
                total += 1
            else:
                mismatched_statuses.append(
                    f'Статус из списка: {status_from_pep_list}; '
                    f'Статус на странице {link}: {status_from_pep_page}'
                )
    if mismatched_statuses:
        logging.info(f'НЕСОВПАДЕНИЕ СТАТУСОВ! {mismatched_statuses}')
    return [
        ('Статус', 'Количество'),
        *status_num.items(),
        ('Total', total)
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()

    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
