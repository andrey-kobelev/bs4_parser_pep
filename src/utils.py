from requests import RequestException

from bs4 import BeautifulSoup

from exceptions import ParserFindTagException
from constants import ENCODING


REQUEST_EXCEPTION = (
    'Возникла ошибка при загрузке страницы {url}'
)
FIND_TAG_EXCEPTION = 'Не найден тег {tag} {attrs}'


def get_response(session, url, encode=ENCODING):
    try:
        response = session.get(url)
        response.encoding = encode
        if response is None:
            raise RequestException()
        return response
    except RequestException:
        raise RequestException(
            REQUEST_EXCEPTION.format(
                url=url
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


def get_soup(response):
    return BeautifulSoup(response.text, features='lxml')
