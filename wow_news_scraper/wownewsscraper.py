import aiohttp
import asyncio
import config as cfg
from bs4 import BeautifulSoup

# A module that asynchronously scrapes every article from the WoW News website


# Scrapes the latest article regardless of article type
async def scrape_latest_article():
    return await scrape_url_via_selector(cfg.css_selectors['NEWS_URL'] + '?page=1', cfg.css_selectors['LATEST_ARTICLE_SELECTOR'])

# Scrapes all articles up until the last article page
async def scrape_articles(quiet=True):
    articles = []
    url = cfg.css_selectors['NEWS_URL']
    page_urls = [f'{url}?page={page_number}' for page_number in range(1, await find_last_page_number() + 1)]
    for page in await scrape_urls(page_urls, quiet):
        articles.extend(_get_articles(page))
    return articles

# Scrapes url and returns specific element viazz selector
async def scrape_url_via_selector(url: str, selector):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            contents = await response.read()
    article = BeautifulSoup(contents.decode('utf-8'), 'lxml').select(selector)
    if article:
        return article.pop()
    else:
        raise InvalidSelectorException

# Scrape all articles from specified page number of WoW News webpage
async def scrape_page(page_number: int, quiet=True):
    return _get_articles((await scrape_urls([f"{cfg.css_selectors['NEWS_URL']}?page={page_number}"], quiet))[0])

# Scrapes HTML data from list of urls
async def scrape_urls(urls: list, quiet=True):
    tasks = []
    if urls:
        for url in urls:
            tasks.append(_scrape_url_task(url, quiet))
        return await asyncio.gather(*tasks)
    else:
        print('WoWNewsScraper.scrape_urls: could not scrape list of urls')
        return None

# Finds and returns the WoW News last page number as an integer
async def find_last_page_number() -> int:
    url = f"{cfg.css_selectors['NEWS_URL']}{'?page=9000'}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return int(response.url.query_string.split('=')[1])
            else:
                print(f'Error in finding last page number. Response Status: {response.status}')

# Helper function that scrapes a single url for HTML data
async def _scrape_url_task(url: str, quiet=True):
    if not quiet: print(f'Downloading articles from {url}')
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            page = await response.read()
    return page

# Helper function that selects each article from a WoW News page and returns a list of HTML data
def _get_articles(page_contents):
    article_list = BeautifulSoup(page_contents.decode('utf-8'), 'lxml').select(cfg.css_selectors['ALL_ARTICLES_SELECTOR'])
    return [str(article) for article in article_list]

class InvalidSelectorException(Exception):
    """
    The used selector did not yield and elements.
    """
    pass