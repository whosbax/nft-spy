"""Jpgstore spy"""
import sys
import traceback
import time
import os
import logging
import requests
from datetime import datetime
import pytz
import pymongo
from db.mongo import DbMongo
import yaml
from spies.a_spy import ASpy
from spies.i_spy import ISpy
from utils.trace import Trace


class JpgStoreApi(ASpy, ISpy):
    """JpgStorApi handler
    """

    DOMAIN_SERVICE = "https://server.jpgstoreapis.com"
    URL_PATTERN = "{}/policy/{}/{}?page={}&sortBy=price-low-to-high"
    URL_VERIFIED_COLLECTION = "{domain}/policy/verified?page=1"
    SALES_ACTION = "sales"
    LISTINGS_ACTION = "listings"
    TIME_ZONE = 'UTC'
    CONFIG = None
    SLEEP_REQ_API = 10
    SLEEP_PROCESS_API = 30

    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.mongo_client = \
            DbMongo.load_db("{}_db".format(self.__class__.__name__))
        if (JpgStoreApi.CONFIG is None):
            JpgStoreApi.loadConfig()

    def get_db(self):
        return self.mongo_client

    def i_get_collections(self) -> any:
        """
        Get collections
        """
        return JpgStoreApi.CONFIG['collections']

    @Trace()
    def get_collection(
        self,
        policy: str,
        action: str,
        cached: bool = False
    ) -> any:
        """
        Get collection
        """
        action = JpgStoreApi.LISTINGS_ACTION \
            if (action is None) else action

        db_collection_name = "{}_{}".format(
            action,
            policy
        )
        collection_exist = \
            bool(len(list(self.mongo_client[db_collection_name].find({}))))
        self._logger.debug("Try get collection from DB[{}]".format(cached))
        self._logger.debug("Collection exist[{}]".format(collection_exist))
        if (not cached or not collection_exist):
            cursor = 1
            has_results = True
            has_error = False
            while (has_results and not has_error):
                self._logger.debug("Start api request")
                time.sleep(JpgStoreApi.SLEEP_REQ_API)
                url = self.get_url_action(policy, action, cursor)
                response = requests.get(url)
                self._logger.debug("Crawling[{}]".format(url))
                cursor = cursor + 1
                json_collection = response.json()
                has_results = bool(len(json_collection))
                has_error = bool("error" in json_collection)
                self._logger.debug("response[{}]".format(json_collection))
                if (has_results and not has_error):
                    for asset in json_collection:
                        self.insert_asset(policy, asset)
                elif has_error:
                    self._logger.error(
                        "response api error[{}]"
                        .format(json_collection['error'])
                    )
                    self._logger.debug("to do try with new ip...")
                else:
                    self._logger.debug("Next collection...")
                    json_collection = {}
        else:
            json_collection = self.mongo_client[db_collection_name].find({})
        return json_collection

    def get_url_action(
        self,
        policy: str,
        action: str = None,
        cursor=1
    ) -> str:
        action = JpgStoreApi.LISTINGS_ACTION \
            if (action is None) else action
        return JpgStoreApi.URL_PATTERN.format(
            JpgStoreApi.DOMAIN_SERVICE,
            policy,
            action,
            cursor
        )

    @Trace()
    def get_last_record(self, policy: str, asset_id: str) -> any:
        """Get last asset histo"""

        db_asset = None
        db_filter = {'asset_id': asset_id}
        for db_a in self.mongo_client[policy]. \
            find(db_filter).\
                sort("confirmed_at", pymongo.DESCENDING).limit(1):
            self._logger.debug("last record db_asset[{}]".format(db_a))
            db_asset = db_a
        return db_asset

    @Trace()
    def insert_asset(self, policy: str, asset) -> any:
        db_collection_listing = "{}_{}".format(
            JpgStoreApi.LISTINGS_ACTION,
            policy
        )
        asset_id = asset['asset_id']
        price_lovelace = asset['price_lovelace']
        confirmed_at = asset['confirmed_at']
        db_filter = {
            'asset_id': asset_id,
            'confirmed_at': confirmed_at
        }
        db_asset = \
            self.mongo_client[db_collection_listing].find_one(db_filter)
        if (db_asset):
            self._logger.debug("Asset exist, nothing to do...")
            return False

        last_record = self.get_last_record(
            policy,
            asset
        )
        self._logger.debug(
            "asset db:[{db_asset}] fresh[{fresh_asset}]".format(
                db_asset=db_asset,
                fresh_asset=asset
            )
        )
        if (last_record):
            self._logger.debug(
                "{display_name}: \
                {last_price}->{new_price}".format(
                    display_name=asset['display_name'],
                    last_price=db_asset['price_lovelace'],
                    new_price=asset['price_lovelace']
                )
            )
            if (last_record['price_lovelace'] > price_lovelace):
                self._logger.debug('PRICE DOWN !')
            else:
                self._logger.debug('PRICE UP !')
        else:
            self._logger.debug("New saved asset[{}]".format(
                asset
            ))
        dt = datetime.now(pytz.timezone(JpgStoreApi.TIME_ZONE))
        self.mongo_client[db_collection_listing].insert_one(
                    {**asset, **{'last_update':  dt}}
        )
        return True

    def i_get_listings(self, policy: str, cached: bool = False):
        """
        Get listing of collections
        """
        return self.get_collection(policy, JpgStoreApi.LISTINGS_ACTION, cached)

    @Trace()
    def i_get_sales(self, policy: str, cached: bool = False):
        """
        Get collection sales
        """
        return self.get_collection(policy, JpgStoreApi.SALES_ACTION, cached)

    @Trace()
    @classmethod
    def loadConfig(cls) -> any:
        yaml_cfg = None
        current_path = os.path.dirname(os.path.realpath(__file__))
        config_path = "{}/config/config.yml".format(current_path)
        with open(config_path, "r") as ymlfile:
            yaml_cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        if (cls.CONFIG is None):
            cls.CONFIG = yaml_cfg
        return yaml_cfg

    @Trace()
    def get_asset_history(self, policy: str, asset_id: str):
        db_collection_listing = "{}_{}".format(
            JpgStoreApi.LISTINGS_ACTION,
            policy
        )
        db_filter = {'asset_id': asset_id}
        return self.mongo_client[db_collection_listing].find(
            db_filter, {
                "price_lovelace": True,
                "confirmed_at": True,
                "last_update": True,
                "display_name": True
            }
        ).sort("confirmed_at", pymongo.DESCENDING)

    def process(self) -> any:
        collections = self.i_get_collections()
        for policy in collections:
            self._logger.debug("Get collection[{}]".format(policy))
            try:
                self.i_get_listings(policy)
            except Exception as exc:
                self._logger.error(exc)
                traceback.print_exception(*sys.exc_info())
