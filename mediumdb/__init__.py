__site_url__ = 'https://medium.com'
__base_url__ = 'https://api.medium.com/v1'

import urllib
from tqdm import tqdm

from metadrive._requests import get_session
from metadrive._bs4 import get_soup
from metadrive.auth import UserAgents, RequestsCookieAuthentication

proxies = {
    'http': 'socks5h://127.0.0.1:9999',
    'https': 'socks5h://127.0.0.1:9999'
}

def login(raw_cookie=None, key_name='medium', proxies=None):
        return RequestsCookieAuthentication(
            raw_cookie, key_name).authenticate()

def harvest():
    anonymous_session = get_session()
    private_session = login(key_name='medium-lys')
    private_limit = 50

    # STEP-1: Get Topic URLs
    items = []

    categories = get_soup(
        'https://medium.com/topics',
        session=anonymous_session,
        update_headers={'User-Agent': UserAgents.random_android()},
        proxies=proxies)

    for category in tqdm(categories.find_all('a', {'class': 'u-backgroundCover'})):
        category_url = category.attrs['href']
        category_name = category.attrs['aria-label']

        articles = get_soup(
            category_url,
            session=anonymous_session,
            update_headers={'User-Agent': UserAgents.random_android()},
            proxies=proxies
        )

        for article in articles.find_all("a", href=lambda href: href and href.startswith('/p/')):
            items.append({
                'url': urllib.parse.urljoin(__site_url__, article.attrs['href']),
                'category': {
                    'name': category_name,
                    'url': category_url}})

    # PART 2 - Retrieval of details.
    for i, item in enumerate(items):

        soup = get_soup(
            urllib.parse.urljoin(__site_url__, item['url']),
            session=private_session,
            update_headers={'User-Agent': UserAgents.random_android()},
            proxies=proxies)

        paywalled = soup.find(
            'div', {
                'class': 'postFade uiScale uiScale-ui--regular uiScale-caption--regular js-regwall'
            })

        if paywalled:
            info = {'paywalled': True}

            if private_limit > 0:
                soup = get_soup(
                    urllib.parse.urljoin(__site_url__, item['url']),
                    session=private_session,
                    update_headers={'User-Agent': UserAgents.random_android()},
                    proxies=proxies)
                private_limit -= 1

                paywalled = soup.find(
                    'div', {
                        'class': 'postFade uiScale uiScale-ui--regular uiScale-caption--regular js-regwall'
                    })

                if paywalled:
                    info.update({'solved-by-cookie': False})
                else:
                    info.update({'solved-by-cookie': True})
            else:
                info.update({'solved-by-cookie': False})
                info.update({'reason': '>50 private uses of private cookie'})

        else:
            info = {'paywalled': False}

        # TITLE
        title = soup.find('h1')
        if title:
            title = title.text

        # BODY
        main = soup.find('main', {'role': 'main'})
        body_html, body_text, sections_with_images = (None, None, None)
        if main:
            body_html = '\n'.join([repr(_) for _ in main.find_all('p')])
            body_text = '\n'.join([_.text for _ in main.find_all('p')])
            sections = soup.find_all('div', 'section-inner sectionLayout--insetColumn')
            sections_with_images = []
            for section in sections:
                section_images = section.find_all('img', 'graf-image')
                section_html ='\n'.join([repr(_) for _ in section.find_all('p')])
                section_text = '\n'.join([_.text for _ in section.find_all('p')])
                sections_with_images.append(
                    {'html': section_html,
                     'text': section_text,
                     'images': [im.attrs for im in section_images]})

        # IMAGE
        cover_image = soup.find('meta', {'property': 'og:image'})
        if cover_image:
            cover_image_url = cover_image.attrs['content']
        else:
            cover_image_url = None

        # AUTHOR
        author_image = main.find('img', {'class': 'avatar-image'})
        author_image_url, author_image_link_name = (None, None)
        if author_image:
            author_image_url = author_image.attrs['src']
            author_image_link_name = author_image.attrs['alt']

        items[i].update({
            'url': urllib.parse.urljoin(__site_url__, items[i]['url']),
            'title': title,
            'body_html': body_html,
            'body_text': body_text,
            'cover_image_url': cover_image_url,
            'author_image_url': author_image_url,
            'author_image_link_name': author_image_link_name,
            'sections': sections_with_images,
            'info': info
        })

        yield item
