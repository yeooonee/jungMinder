from pymongo import MongoClient
from ref.config import Config

client = MongoClient(Config.MONGO_URI)
db = client.dbjungminder