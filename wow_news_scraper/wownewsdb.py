import asyncio
import datetime
import config as cfg
from motor import motor_asyncio
from logger import InfoBotLogger


class WoWNewsDB:
    def __init__(self):
        self._client = motor_asyncio.AsyncIOMotorClient(cfg.mongodb_atlas['connection_string'])
        self._database = self.client[cfg.mongodb_atlas['database_name']]
        self._news_collection = self.database[cfg.mongodb_atlas['news_collection_name']]
        self._logger = InfoBotLogger(self.client)

    async def has_id(self, article_id: list):
        return await self._news_collection.find_one({cfg.article_keys['ID']: article_id})

    @property
    def client(self):
        return self._client

    @property
    def database(self):
        return self._database

    @property
    def news_collection(self):
        return self._news_collection

    @property
    def logger(self):
        return self._logger

    # Returns the latest article that can either be a Hotfixes/Update or Regular article
    @property
    async def latest(self):
        return await self.get_latest_article()

    # Insert article documents into the WoW News collection
    async def insert_articles(self, articles, verbose=False):
        try:
            if type(articles) == list or type(articles) == dict:
                if type(articles) == dict:
                    articles = list(articles)
                result = await self.news_collection.insert_many(articles)
                # If documents were successfully created then log the resulting _id list
                if result:
                    if verbose is True:
                        print(f'Article(s) Inserted: {result.inserted_ids}')
                    await self.logger.log_database_insert(ids=result.inserted_ids)
                    return result.inserted_ids
                else:
                    raise Exception
        except Exception as e:
            print(f'WoWNewsDB.insert_articles: An exception occured during insertion to DB.\n{e}')

    # Archives any existing articles with the same article_id and deletes them fromm the active news database.
    async def update_by_article_type(self, articles: list, verbose=False):
        try:
            if type(articles) == list or type(articles) == dict:
                if type(articles) == dict:
                    articles = [articles]
                    # Update articles that changed
                for article in articles:
                    await self.news_collection.update_one({cfg.article_keys["TYPE"]: article[cfg.article_keys["TYPE"]]}, 
                        {               
                            '$set': 
                                {
                                    cfg.article_keys["TYPE"]: article[cfg.article_keys["TYPE"]],
                                    cfg.article_keys['TITLE']: article[cfg.article_keys['TITLE']],
                                    cfg.article_keys['DESCRIPTION']: article[cfg.article_keys['DESCRIPTION']],
                                    cfg.article_keys['DATETIME']: article[cfg.article_keys['DATETIME']],
                                    cfg.article_keys['URL']: article[cfg.article_keys['URL']],
                                    cfg.article_keys['IMAGE_URL']: article[cfg.article_keys['IMAGE_URL']]
                                }
                        })
                    await self.logger.log_database_update(article_type=article[cfg.article_keys['TYPE']], article_title=article[cfg.article_keys['TITLE']])
            else:
                raise Exception
        except Exception as e:
            print(f'WoWNewsDB.update_by_article_type: An exception occured during an update to DB.\n{e}')

    # Returns the latest article regardless of article type (Hotfixes/Update or Regular)
    async def get_latest_article(self):
        try:
            articles = self.news_collection.aggregate([
                {
                    '$sort': {cfg.article_keys['DATETIME']: -1}
                },
                {
                    '$limit': 1
                }
            ])
            if articles:
                article = await articles.to_list(length=None)
                if len(article) == 1:
                    return article.pop()
                else:
                    return None
            else:
                return None
        except Exception as e:
            print('WoWNewsDB.get_latest: could not aggregate the latest WoW news article from database', e)

    # Returns datetime object with respect to year, month and day values
    def date_time(self, year, month, day):
        return datetime.datetime(year=year, month=month, day=day)

    # Return a list of database names
    async def list_database_names(self):
        return await self.client.list_database_names()

    # Return a list of collection names
    async def list_collection_names(self):
        return await self.database.list_collection_names()


class ArticlesNotFound(Exception):
    pass

class IncorrectType(Exception):
    pass