__site_url__ = 'https://medium.com'
__base_url__ = 'https://api.medium.com/v1'

# from metadrive._selenium import get_driver
# driver = get_driver(proxies={'socks_proxy': '127.0.0.1:9999'})
# driver.get(__site_url__)
# driver.get('https://www.whatismyip.com')

from metadrive._requests import get_session
from metadrive._bs4 import get_soup

from metadrive import utils
from metadrive.auth import RequestsCookieAuthentication

import json
from urllib.parse import urljoin
import time


def login(raw_cookie=None, key_name='medium', proxies=None):
    return RequestsCookieAuthentication(
        raw_cookie, key_name).authenticate()

def harvest(query=None, limit=None, proxies=None):

    # url = 'https://medium.com/mit-technology-review/the-biggest-technology-failures-of-2018-52eaf050751a'
    # body = soup.find('main', {'role': 'main'}).text

    print("Getting anonymous session...")
    anonymous_session = get_session()

    print("Getting private session...")
    private_session = login(key_name='medium-lys', proxies=proxies)
    private_limit = 50

    print("Getting categories... ", end='')
    categories = get_soup(urljoin(__site_url__, 'topics'), anonymous_session, proxies=proxies)
    print("done")

    items = []

    # getting items
    print("Getting visitable urls... ")
    for category in categories.find_all('a', {'class': 'u-backgroundCover'}):
        print('|', end='')
        soup = get_soup(category.attrs['href'], anonymous_session, proxies=proxies)

        for article in soup.find_all("a", href=lambda href: href and href.startswith('/p/')):

            item = {
                'name': article.text,
                'url': article.attrs['href'],
                'category': {
                    'name': category.text,
                    'url': category.attrs['href']}}

            items.append(item)
        time.sleep(1)

    # updating items
    for i, item in enumerate(items):
        print('.', end='')
        info = {'status': 'ok'}

        soup = get_soup(item['url'], anonymous_session, proxies=proxies)

        paywalled = soup.find('div', {'class':'postFade uiScale uiScale-ui--regular uiScale-caption--regular js-regwall'})

        if paywalled:
            if private_limit > 0:

                soup = get_soup(item['url'], private_session, proxies=proxies)
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

