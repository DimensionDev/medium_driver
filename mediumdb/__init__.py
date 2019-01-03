__site_url__ = 'https://medium.com'
__base_url__ = 'https://api.medium.com/v1'

from metadrive._requests import get_session
from metadrive import utils
import bs4

def login(raw_cookie=None):

    requests = get_session()

    if raw_cookie is not None:
        requests.headers.update({
            'content-type':'text/plain',
            'cookie': raw_cookie
        })

    return requests


def harvest(query=None, limit=None):

    requests = login()

    url = 'https://medium.com/mit-technology-review/the-biggest-technology-failures-of-2018-52eaf050751a'

    response = requests.get(url)

    if response.ok:
        data = response.content
        soup = bs4.BeautifulSoup(data, 'html.parser')

        body = soup.find('main', {'role': 'main'}).text

        yield {
            'body': body,
            '-': url
        }
