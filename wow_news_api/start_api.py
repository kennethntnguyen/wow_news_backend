from flask import Flask, jsonify
from flask_pymongo import PyMongo
from bson.json_util import dumps
import config as cfg

# Initialize App
app = Flask(__name__)

# MongoDB Credentials
app.config['MONGO_URI'] = cfg.mongodb_atlas['connection_string']
mongo = PyMongo(app)
news_collection = mongo.cx[cfg.mongodb_atlas['database_name']][cfg.mongodb_atlas['news_collection_name']]

@app.route('/')
def home_page():
  return('<h1>Welcome to WoW News API</h1>')

@app.route('/<article_type>')
def article_by_type(article_type):
  return dumps(news_collection.find_one_or_404({cfg.article_keys['TYPE']: article_type}))

# Run Server in Development Mode
if __name__ == '__main__':
  app.run(port=8080)
