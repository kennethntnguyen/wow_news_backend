import config as cfg
import datetime
import html
import regex as re
from bs4 import BeautifulSoup

class WowNewsWrangler():
    def __init__(self, error_logger):
        self._error_logger = error_logger
        self.article_id_pattern = re.compile(cfg.regex_patterns['ARTICLE_ID_PATTERN'])
        self.title_pattern = re.compile(cfg.regex_patterns['TITLE_PATTERN'])
        self.description_pattern = re.compile(cfg.regex_patterns['DESCRIPTION_PATTERN'], flags=re.DOTALL)
        self.datetime_pattern = re.compile(cfg.regex_patterns['DATE_PATTERN'])
        self.url_pattern = re.compile(cfg.regex_patterns['URL_PATTERN'])
        self.image_url_pattern = re.compile(cfg.regex_patterns['IMAGE_PATTERN'])

    @property
    def error_logger(self):
        return self._error_logger

    def wrangle_articles(self, articles: list) -> list:
        if type(articles) == list and len(articles) == 0:
            raise EmptyArticleList
        elif type(articles) is not list:
            articles = [str(articles)]

        if type(articles) == list and 0 < len(articles):
            keys = cfg.article_keys.values()
            null_articles = dict(zip(keys, [[] for _ in range(len(keys))]))
            wrangled_articles = []
            for article in articles:
                if type(article) is not str:
                    article = str(article)
                clear = True
                article_data = self.extract_article_data(article)
                for key in article_data.keys():
                    if article_data[key] is None:
                        null_articles[key].append(article)
                        clear = False
                if clear:
                    wrangled_articles.append(article_data)
            num_of_null_articles = sum([len(value) for value in null_articles.values()])
            if num_of_null_articles:
                self.error_logger.log_error(error='null_articles', module='wownewswrangler', error_description=null_articles, notes=f'{num_of_null_articles} articles have null values')
            return wrangled_articles
        else:
            return list()


    def extract_article_data(self, article: str):
        return {
                #cfg.article_keys['ID']: self.get_id(article),
                cfg.article_keys['TITLE']: self.get_title(article),
                cfg.article_keys['DESCRIPTION']: self.get_descrition(article),
                cfg.article_keys['DATETIME']: self.get_datetime(article),
                cfg.article_keys['URL']: self.get_url(article),
                cfg.article_keys['IMAGE_URL']: self.get_image(article)}


    def get_id(self, article: str):
        if type(article) == str:
            url_result = re.search(self.url_pattern, html.unescape(article))
            if url_result:
                id_result = re.search(self.article_id_pattern, url_result.group())
                if id_result:
                    return int(id_result.group())
                return None
            else:
                return None
        else:
            return None


    def get_url(self, article: str):
        if type(article) == str:
            result = re.search(self.url_pattern, html.unescape(article))
            if result:
                string = result.group()
                if string.startswith('http'):
                    return string
                else:
                    return f"{cfg.regex_patterns['URL']}{result.group()}"
            else:
                return None
        else:
            return None


    def get_image(self, article: str):
        if type(article) == str:
            result = re.search(self.image_url_pattern, html.unescape(article))
            if result:
                return f'{"https:"}{result.group()}'
            else:
                return None
        else:
            return None


    def get_title(self, article: str):
        if type(article) == str:
            result = re.search(self.title_pattern, html.unescape(article))
            if result:
                return self.strip_LR_whitespaces(result.group())
            else:
                return None
        else:
            return None


    def get_descrition(self, article: str):
        if type(article) == str:
            result = re.search(self.description_pattern, html.unescape(article))
            if result:
                return self.strip_LR_whitespaces(result.group())
            else:
                return None
        else:
            return None


    def get_datetime(self, article: str):
        if type(article) == str:
            result = re.search(self.datetime_pattern, html.unescape(article))
            if result:
                try:
                    return datetime.datetime.strptime(result.group(), '%Y-%m-%dT%H:%M:%S.%fZ')
                except Exception:
                    print(
                        'WoWNewsWrangler.get_date: could not convert date-time string to datetime object')
                    return None
            else:
                return None
        else:
            return None

    def strip_LR_whitespaces(self, string):
        return string.strip()

    def is_hotfixes_title(self, title: str):
        #title_words = re.sub(cfg.regex_patterns['SPECIAL_CHARACTERS_AND_SPACE'], ' ', title).lower().split(' ')
        hit_words = ['update', 'hotfix']
        return any([hit_word in title.lower() for hit_word in hit_words])

class EmptyArticleList(Exception):
    pass

class ArticleTypeError(Exception):
    pass