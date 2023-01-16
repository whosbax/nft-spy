import copy
from flask import Flask
from spies.jpgstoreapis.jpgstoreapis import JpgStoreApi
app = Flask(__name__)


@app.route('/')
def home(name):
    return 'hello world'


@app.route(
    '/policy/<policy>/asset/<asset>/style/<style>',
    methods=['POST', 'GET']
)
@app.route(
    '/policy/<policy>/asset/<asset>',
    methods=['POST', 'GET']
)
def show_asset_history(policy, asset, style='bar'):
    spy_jpg_store = JpgStoreApi()
    chart_template = {
        "type": style,
        "data": {
            "labels": [],
            "datasets": [
                {
                    "data": [],
                    "borderWidth":1
                }
            ]
        },
        'options': {
            'parsing': {
                'xAxisKey': 'asset.confirmed_at',
                'yAxisKey': 'asset.price'
            },
            'animations': {
                'tension': {
                    'duration': '1000',
                    'easing': 'linear',
                    'from': 1,
                    'to': 0,
                    'loop': 'false'
                }
            },
            'plugins': {
                'tooltip': {
                    'callbacks': {
                        'footer': {},
                    }
                }
            }
        },
    }
    html = \
        "<script src='https://cdn.jsdelivr.net/npm/chart.js'></script> \n"
    datas = spy_jpg_store.get_asset_history(policy=policy, asset_id=asset)
    file_template = open("template.html", "rt")
    html_template = file_template.read()
    html_template = html_template.replace(
        '#COL#', str(policy).join([i for i in policy if not i.isdigit()])
    )
    chart = copy.deepcopy(chart_template)
    i = 0
    assets = []
    for asset_histo in datas:
        asset_histo.pop('_id')
        asset_histo.pop('last_update')
        if (not i):
            chart['data']['datasets'][0]['label'] = \
                asset_histo['display_name'] + "_" + str(policy)
        price = str(int(asset_histo['price_lovelace'])//1000000)
        asset_histo['price'] = price
        assets.append({
            'asset': asset_histo
            }
        )
    chart['data']['datasets'][0]['data'] = \
        sorted(assets, key=lambda asset: asset['asset']['price'])
    html_template = html_template.replace(
        '#CHART#', str(chart)
    )
    file_template.close()
    html = html + html_template

    return html


@app.route(
    '/all',
    methods=['POST', 'GET'],
)
@app.route(
    '/all/limit/<limit>',
    methods=['POST', 'GET'],
)
@app.route(
    '/all/limit/<limit>/style/<style>',
)
def show_all(limit=None, style='bar'):
    spy_jpg_store = JpgStoreApi()
    chart_template = {
        "type": style,
        "data": {
            "labels": [],
            "datasets": [
                {
                    "data": [],
                    "borderWidth":1
                }
            ]
        },
        'options': {
            'parsing': {
                'xAxisKey': 'asset.display_name',
                'yAxisKey': 'asset.price'
            },
            'plugins': {
                'tooltip': {
                    'callbacks': {
                        'footer': {},
                    }
                }
            }
        },
    }

    html = ""
    for collection in spy_jpg_store.CONFIG['collections']:
        cursor = 0
        file_template = open("template.html", "rt")
        html_template = file_template.read()
        col_js_id = ""\
            .join([char for char in collection if not char.isdigit()])
        html_template = html_template.replace(
            '#COL#', col_js_id
        )
        chart = copy.deepcopy(chart_template)
        chart['data']['datasets'][0]['label'] = "Policy: {}".format(collection)
        assets = []
        list_col = spy_jpg_store.i_get_listings(collection, cached=True)
        sorted_list_col = sorted(list_col, key=lambda asset: int(asset['price_lovelace']))
        for asset in sorted_list_col:
            asset.pop('_id')
            asset.pop('last_update')
            if limit and cursor == int(limit):
                break
            cursor = cursor + 1
            price = int(int(asset['price_lovelace'])//1000000)
            asset['price'] = price
            assets.append({'asset': asset})
        chart['data']['datasets'][0]['data'] = assets
        html_template = html_template.replace(
            '#CHART#', str(chart)
        )
        file_template.close()
        html = html + html_template
    html = \
        "<script \
        src='https://cdn.jsdelivr.net/npm/chart.js'> \n" + \
        "</script> \n" + html

    return html


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
