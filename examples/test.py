import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
print(parent)
sys.path.append(parent)
#sys.path.append("{}/spies/".format(parent))
sys.path.append("{}/spies/jpgstoreapis/".format(parent))
sys.path.append("{}/db/mongo/".format(parent))

from jpgstoreapis import JpgStoreApi

from urllib.parse import quote_plus

spy = JpgStoreApi()
policy="86ec26a91051e4d42df00b023202e177a0027dca4294a20a0326a116"


fresh_col=spy.i_get_listings(policy,JpgStoreApi.LISTINGS_ACTION, True)

for asset in fresh_col:
    spy.update_asset(policy,asset)

cached_col=spy.i_get_listings(policy, JpgStoreApi.LISTINGS_ACTION, True)
for asset in cached_col:
    print(asset)


#print("fresh_col: {}".format(len(fresh_col)))
#print("cached_col: {}".format(len(list(spy.i_get_listings(policy, JpgStoreApi.LISTINGS_ACTION, True)))))

a={'asset_id': '86ec26a91051e4d42df00b023202e177a0027dca4294a20a0326a116617175616661726d657236313333', 'display_name': 'Aquafarmer #6133', 'tx_hash': '6015a855e2c2bd773a66ac518fe5236eae1e9b7b3889edf0d6b2dd253e60011a#0', 'listing_id': 21111523, 'listed_at': '2022-12-29T15:46:55.815Z', 'price_lovelace': '3327', 'listing_type': 'SINGLE_ASSET'}
spy.update_asset(policy,a)


fresh_col=spy.i_get_listings(policy,JpgStoreApi.SALES_ACTION)
for asset in fresh_col:
    spy.update_asset(policy,asset)
cached_col=spy.i_get_listings(policy, JpgStoreApi.SALES_ACTION, True)
for asset in cached_col:
    print(asset)