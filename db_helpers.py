# db_helpers.py
from pymongo import MongoClient
import config

client = MongoClient(config.MONGO_URI)

db = client[config.MONGO_DB_NAME]

def get_collection(name: str):
    return db[name]
