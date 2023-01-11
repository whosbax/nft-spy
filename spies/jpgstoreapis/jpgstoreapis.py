"""Jpgstore spy"""

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
    URL_PATTERN = "{}/policy/{}/{}?page=1&sortBy=price-low-to-high"
    URL_VERIFIED_COLLECTION = "{domain}/policy/verified?page=1"
    SALES_ACTION = "sales"
    LISTINGS_ACTION = "listings"
    TIME_ZONE = 'UTC'
    CONFIG = None

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
        json_collection = None
        db_collection_name = "{}_{}".format(
            action,
            policy
        )
        collection_exist = \
            len(list(self.mongo_client[db_collection_name].find({})))
        if (cached is False or
                not collection_exist):
            response = requests.get(
                self.get_url_action(policy, action)
            )
            json_collection = response.json()
            logging.debug("response[{}]".format(json_collection))
            if (json_collection and "error" not in json_collection):
                dt = datetime.now(pytz.timezone(JpgStoreApi.TIME_ZONE))
                json_collection = list(map(
                        lambda asset: {**asset, **{'last_update':  dt}},
                        json_collection
                    ))
                if (not collection_exist):
                    logging.debug(
                        "insert {action} collection: {policy}".format(
                            action=action,
                            policy=policy
                        )
                    )
                    self.mongo_client[db_collection_name]\
                        .insert_many(json_collection)
            else:
                json_collection = {}
        else:
            json_collection = self.mongo_client[db_collection_name].find({})
        return json_collection

    def get_url_action(self, policy: str, action: str = None) -> str:
        action = JpgStoreApi.LISTINGS_ACTION \
            if (action is None) else action
        return JpgStoreApi.URL_PATTERN.format(
            JpgStoreApi.DOMAIN_SERVICE,
            policy,
            action
        )

    @Trace()
    def update_asset(self, policy: str, asset) -> any:
        db_collection_listing = "{}_{}".format(
            JpgStoreApi.LISTINGS_ACTION,
            policy
        )
        asset_id = asset['asset_id']
        price_lovelace = asset['price_lovelace']
        db_filter = {'asset_id': asset_id}
        db_asset = self.mongo_client[db_collection_listing].find_one(db_filter)
        if (db_asset):
            if (db_asset['price_lovelace'] != price_lovelace):
                if (db_asset['price_lovelace'] > price_lovelace):
                    logging.debug("Last price {display_name}: {last_price}\
                         New price: {new_price}".format(
                            display_name=asset['display_name'],
                            last_price=db_asset['price_lovelace'],
                            new_price=asset['price_lovelace']
                        )
                    )
                logging.debug(
                    "asset db:[{db_asset}] fresh[{fresh_asset}]".format(
                        db_asset=db_asset,
                        fresh_asset=asset
                    )
                )
                logging.debug(
                    "Updated asset:\
{asset_id} from {policy}\nPrice {last_price}->{new_price}"
                    .format(
                        asset_id=asset['asset_id'],
                        policy=policy,
                        last_price=db_asset['price_lovelace'],
                        new_price=asset['price_lovelace']
                    )
                )
            else:
                logging.debug("Same price, nothing to do...")
                return False
        else:
            logging.debug("New saved asset[{}]".format(
                asset
            ))
        dt = datetime.now(pytz.timezone(JpgStoreApi.TIME_ZONE))
        self.mongo_client[db_collection_listing].insert_one(
                    {**asset, **{'last_update':  dt}}
        )

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
                "last_update": True,
                "display_name": True
            }
        ).sort("last_update", pymongo.DESCENDING)

    def process(self) -> any:
        collections = self.i_get_collections()
        for policy in collections:
            for asset in self.i_get_listings(
                policy, JpgStoreApi.LISTINGS_ACTION
            ):
                self.update_asset(policy, asset)
