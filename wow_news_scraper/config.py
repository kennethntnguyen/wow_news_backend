import os

mongodb_atlas = {
    "connection_string": os.environ.get('MONGODB_CONNECTION_STRING'),
    "database_name": "info-bot",
    "news_collection_name": "wow-news",
    "log_collections": {"errors": "wow-error-log", "CRUDops": "CRUD-log"},
    "update_rate": 60
}

article_types = {
    "HOTFIXES": "hotfixes",
    "LATEST": "latest"
}

article_keys = {
    "TYPE": "type",
    "ID": "_id",
    "TITLE": "title",
    "DESCRIPTION": "description",
    "DATETIME": "datetime",
    "URL": "url",
    "IMAGE_URL": "image_url"
}

css_selectors = {
    "NEWS_URL": "https://worldofwarcraft.com/en-us/news",
    "ALL_ARTICLES_SELECTOR": "#main > div > div.Pane-content > div > div.Pane-content > div.Pane.Pane--transparent > div.Pane-content > div > div.List.List--vertical.List--separatorAll.List--full > div.List-item",
    "LATEST_ARTICLE_SELECTOR": "#main > div > div.Pane-content > div > div.Pane-content > div.Pane.Pane--transparent > div.Pane-content > div > div.List.List--vertical.List--separatorAll.List--full > div:nth-child(1)"
}

regex_patterns = {
    "URL": 'https://worldofwarcraft.com',
    "ARTICLE_ID_PATTERN": r'[0-9]+',
    "URL_PATTERN": r'(?<=href=\")[^\"]*(?=\")',
    "IMAGE_PATTERN": r'(?<=data-src=")[^"]+(?=")',
    "TITLE_PATTERN": r'(?<=<div[\s]+class="NewsBlog-title">).+(?=</div><p class=")',
    "DESCRIPTION_PATTERN": r'(?<=<p[\s]+class="NewsBlog-desc[\s]+color-beige-medium[\s]+font-size-xSmall">).+[\n]*(?=</p></div><div[\s]+media-large="gutter-normal")',
    "DATE_PATTERN": r'(?<=data-props=\'\{"iso8601":").+(?=","relative")',
    "SPECIAL_CHARACTERS_AND_SPACE": r'[^A-Za-z0-9]+'
}
