import config as cfg
import re
import os
import datetime
from motor import motor_asyncio


class FileLogger:
    def __init__(self, log_filename: str, directory: str = '.', append: bool = True):
        self._filename = self._validate_filename(log_filename)
        self._append = append
        self.file = open(os.path.join(directory, self._filename),
                         self._append_mode(append))

    def __del__(self):
        self.file.close()

    def write(self, line: str):
        self.file.write(line)

    def _validate_filename(self, filename: str):
        if re.search(r'.+\.log', filename):
            return filename
        elif re.search(r'.+\..+', filename):
            return filename
        elif re.search(r'.+', filename):
            return filename + '.log'

    def _append_mode(self, append: bool):
        file_mode = {
            True: 'a',
            False: 'w'
        }
        return file_mode[append]


class InfoBotLogger:
    def __init__(self, motor_client):
        self._client = motor_client
        self._database = self.client[cfg.mongodb_atlas['database_name']]
        # Dictionary of collections that are used to log various database activities
        self._collections = dict(zip(cfg.mongodb_atlas['log_collections'].keys(), [
                                 self.database[collection_name] for collection_name in cfg.mongodb_atlas['log_collections'].values()]))

    @property
    def client(self):
        return self._client

    @property
    def database(self):
        return self._database

    @property
    def collections(self):
        return self._collections

    @property
    def current_pst(self):
        return datetime.datetime.utcnow() - datetime.timedelta(hours=8)

    async def log_database_insert(self, ids: list):
        await self.collections['CRUDops'].insert_one({'operation': 'create', 'number_of_articles': len(ids), 'articles_inserted': ids, 'datetime': self.current_pst})
    
    async def log_database_update(self, article_type: str, article_title: str):
        await self.collections['CRUDops'].insert_one({'operation': 'update', 'article_type_updated': article_type, 'article_title': article_title, 'datetime': self.current_pst})

    async def log_error(self, error: str, module: str, error_description: str, notes: str = None):
        log_dictionary = {'error': error, 'module': module, 'error_description': error_description}
        if notes:
            log_dictionary['notes'] = notes
        await self.collections['errors'].insert_one(log_dictionary)
