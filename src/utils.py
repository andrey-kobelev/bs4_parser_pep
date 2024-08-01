from requests import RequestException

from bs4 import BeautifulSoup

from exceptions import ParserFindTagException


REQUEST_EXCEPTION = (
    'Возникла ошибка при '
    'загрузке страницы {url}: {error}'
)
FIND_TAG_EXCEPTION = 'Не найден тег {tag} {attrs}'


def get_response(session, url, encode='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encode
        return response
    except RequestException as error:
        raise ConnectionError(
            REQUEST_EXCEPTION.format(
                url=url,
                error=error
            )
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(
        tag, attrs=(
            attrs if attrs is not None else {}
        )
    )
    if searched_tag is None:
        raise ParserFindTagException(
            FIND_TAG_EXCEPTION.format(
                tag=tag,
                attrs=attrs
            )
        )
    return searched_tag


def get_soup(session, url, features='lxml'):
    return BeautifulSoup(
        get_response(session, url).text, features=features
    )
