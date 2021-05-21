import asyncio
import config as cfg
import html5lib
import time
import typing
from logger import InfoBotLogger

import wownewsscraper as wns
import wownewswrangler as wnw
from wownewsdb import WoWNewsDB

# Script to start and run the WoW News Database
# Uses code from wownewsscraper, wownewswrangler and wownewsdb. None of those individual modules depend on each other.

wow_newsdb = WoWNewsDB()
logger = InfoBotLogger(motor_client=wow_newsdb.client)
wow_newswrangler = wnw.WowNewsWrangler(logger.collections['errors'])

# Start the WoW News Scraping Service
def start_wns(event_loop):
    event_loop.run_until_complete(updater(event_loop))

async def wow_newsdb_initialized() -> bool:
    return await wow_newsdb.news_collection.count_documents({}) > 0

async def initialize_collection():
    await wow_newsdb.insert_articles(await scrape_new_articles())

async def get_latest_known_article_title():
    return (await wow_newsdb.latest)[cfg.article_keys['TITLE']]

async def scrape_latest_article_title():
    return wow_newswrangler.wrangle_articles(await wns.scrape_latest_article()).pop()[cfg.article_keys['TITLE']]
    

# Scrape the latest non hotfix article and the latest hotfix article
async def scrape_new_articles():
    last_page_number = await wns.find_last_page_number()
    latest_hotfixes_article = None
    latest_non_hotfixes_article = None
    loop = True
    page = 1
    while loop:
        # Stops while loop if current page number exceeds last page number
        if last_page_number < page:
            loop = False
        else:
            # Scrape all articles from current page
            current_page_articles = wow_newswrangler.wrangle_articles(await wns.scrape_page(page))
            i = 0
            N = len(current_page_articles)
            # Iterates through each article
            while loop and i < N:
                # Stops while loop if latest_hotfixes_article and latest_non_hotfixes_article contain articles
                if latest_non_hotfixes_article != None and latest_hotfixes_article != None:
                    loop = False
                current_article_title = current_page_articles[i][cfg.article_keys['TITLE']]
                # If hotfixes article hasn't been found and the current article is a hotfixes article then set latest_hotfixes_article to current article
                if latest_hotfixes_article == None and wow_newswrangler.is_hotfixes_title(current_article_title):
                    latest_hotfixes_article = current_page_articles[i]
                    latest_hotfixes_article[cfg.article_keys['TYPE']] = cfg.article_types['HOTFIXES']
                # Similarly but with latest_non_hotfixes_article
                elif latest_non_hotfixes_article == None and not wow_newswrangler.is_hotfixes_title(current_article_title):
                    latest_non_hotfixes_article = current_page_articles[i]
                    latest_non_hotfixes_article[cfg.article_keys['TYPE']] = cfg.article_types['LATEST']
                i += 1
            page += 1
    return [latest_hotfixes_article, latest_non_hotfixes_article]

    # Continously running function that checks for new articles, it is in charge of archiving and updating new and old articles.
async def updater(event_loop):
    known_latest_article_title = None
    loop = True
    while loop:
        try:
            await asyncio.sleep(cfg.mongodb_atlas['update_rate'])
            # initializing known_latest_article_id value
            if known_latest_article_title == None:
                # checks of news database has been initialized, if not then it will populate database with all current articles
                if not await wow_newsdb_initialized():
                    await initialize_collection()
                known_latest_article_title = await get_latest_known_article_title()
            # known_latest_article_id is instantiated
            latest_article_title = await scrape_latest_article_title()
            print(f'Actual latest: {latest_article_title}\nKnown latest: {known_latest_article_title}')
            if latest_article_title != known_latest_article_title:
                print(f'Article database is not up to date.\nActual latest: {latest_article_title}\nKnown latest: {known_latest_article_title}')
                await wow_newsdb.update_by_article_type(await scrape_new_articles())
                known_latest_article_title = await get_latest_known_article_title()
        except Exception as e:
            print('wownewsservice.updater: error in updater. stoping service', e)
            loop = False
            event_loop.stop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    start_wns(loop)