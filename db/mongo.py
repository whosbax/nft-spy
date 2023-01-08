"""Mongo connexion"""
from pymongo import MongoClient
from dotenv import dotenv_values
import os
from urllib.parse import quote_plus


class DbMongo:
    """DB connexion singleton
    """

    CLIENT = None
    DB = None

    @classmethod
    def load_db(cls, db_name: str):
        #config = dotenv_values(".env")
        if (DbMongo.CLIENT is None):
            DbMongo.CLIENT = MongoClient(
                host="{ip}:27017".format(
                    ip=quote_plus(os.getenv('MONGO_INITDB_IP'))
                ),
                serverSelectionTimeoutMS=3000,
                username="{username}".format(
                    username=quote_plus(os.getenv('MONGO_INITDB_ROOT_USERNAME'))
                ),
                password="{password}".format(
                    password=quote_plus(os.getenv('MONGO_INITDB_ROOT_PASSWORD'))
                )
            )
        return DbMongo.CLIENT[db_name]
