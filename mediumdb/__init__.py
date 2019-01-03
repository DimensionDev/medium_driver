__site_url__ = 'https://medium.com'
__base_url__ = 'https://api.medium.com/v1'

from metadrive._requests import get_session
from metadrive._bs4 import get_soup

from metadrive import utils
from metadrive.auth import RequestsCookieAuthentication

import json
from urllib.parse import urljoin


def login(raw_cookie=None, key_name='medium'):
    session = RequestsCookieAuthentication(raw_cookie, key_name).authenticate()
    return session

def harvest(query=None, limit=None):

    # url = 'https://medium.com/mit-technology-review/the-biggest-technology-failures-of-2018-52eaf050751a'
    # body = soup.find('main', {'role': 'main'}).text

    anonymous_session = get_session()
    private_session = login(key_name='medium-lys')
    private_limit = 50

    categories = get_soup(urljoin(__site_url__, 'topics'), anonymous_session)

    items = []

    # getting items
    for category in categories.find_all('a', {'class': 'u-backgroundCover'}):
        print('|', end='')
        soup = get_soup(category.attrs['href'])

        for article in soup.find_all("a", href=lambda href: href and href.startswith('/p/')):

            item = {
                'name': article.text,
                'url': article.attrs['href'],
                'category': {
                    'name': category.text,
                    'url': category.attrs['href']}}

            items.append(item)

    # updating items
    for i, item in enumerate(items):
        print('.', end='')
        info = {'status': 'ok'}

        soup = get_soup(item['url'], anonymous_session)

        paywalled = soup.find('div', {'class':'postFade uiScale uiScale-ui--regular uiScale-caption--regular js-regwall'})

        if paywalled:
            if private_limit > 0:

                soup = get_soup(item['url'], private_session)
                private_limit -= 1
            else:
                info = {'status': 'run-out-of-personal-limit'}

        items[i].update({'data': repr(soup), 'info': info})

        with open('medium-data.jsonl', 'a') as f:
            f.write(items[i])

    return items

    # Later refactor to use yield gracefully
    #
    # yield {
    #     'name': topic.text,
    #     '-': topic.attrs['url']
    # }

