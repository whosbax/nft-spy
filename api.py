from flask import Flask
from spies.jpgstoreapis.jpgstoreapis import JpgStoreApi
app = Flask(__name__)


@app.route('/')
def home(name):
    return 'hello world'


@app.route('/policy/<policy>/asset/<asset>', methods=['POST', 'GET'])
def show_asset_history(policy, asset):
    spy_jpg_store = JpgStoreApi()
    data = spy_jpg_store.get_asset_history(policy=policy, asset_id=asset)
    asset_name = None
    html_ = ""
    arr_data = "var data = []; \n"
    for asset_h in data:
        if asset_name is None:
            html_ = html_+"data.push({ '" + asset_h['display_name']+"': '" + \
                str(int(0))+"'}); \n"
            asset_name = asset_h['display_name']
        html_ = html_+"data.push({ '" + asset_h['display_name']+"': '" + \
            str(int(asset_h['price_lovelace'])//1000000)+"'}); \n"

    html_template = open("template.html", "rt")
    html_graph = html_template.read()
    html_graph = html_graph.replace('#ARR_DATA_NAME#', "data")
    html_graph = html_graph.replace('#ARR_DATA#', arr_data)
    html_graph = html_graph.replace('#PUSH_DATA#', html_)
    html_graph = html_graph.replace('#DISPLAY_NAME#', asset_name)
    html_graph = html_graph+" </body> \n"
    html_template.close()
    return html_graph


@app.route('/all', methods=['POST', 'GET'], defaults={'limit': None})
@app.route('/all/limit/<limit>', methods=['POST', 'GET'])
def show_all(limit):
    spy_jpg_store = JpgStoreApi()
    all_html = ""
    for collection in spy_jpg_store.CONFIG['collections']:
        i = 0
        for asset in spy_jpg_store.i_get_listings(collection, cached=True):
            if (limit and i == int(limit)):
                break
            i = i+1
            data = spy_jpg_store.get_asset_history(
                policy=collection, asset_id=asset['asset_id']
            )
            asset_name = None
            for asset_h in data:
                arr_data = "var data_"+str(i)+" = []; \n"

                if asset_name is None:
                    asset_name = asset_h['display_name']

                html_ = "data_"+str(i)+".push({ '" + \
                    asset_h['display_name']+"': '" + \
                    str(int(asset_h['price_lovelace'])//1000000)+"'}); \n"

                html_template = open("template.html", "rt")
                html_graph = html_template.read()

                html_graph = html_graph.replace(
                    "<script src='http://unpkg.com/\
candela/dist/candela.min.js' />".strip(),
                    ""
                )
                html_graph = html_graph.replace(
                    '#ARR_DATA_NAME#', "data_" + str(i)
                )
                html_graph = html_graph.replace(
                    '#PUSH_DATA#', html_
                )
                html_graph = html_graph.replace(
                    '#ARR_DATA#', arr_data
                )
                html_graph = html_graph.replace(
                    '#DISPLAY_NAME#', asset_name
                )
                all_html = all_html+html_graph+"\n"
                html_template.close()
    all_html = \
        "<script \
        src='http://unpkg.com/candela/dist/candela.min.js'/> \n" + \
        all_html

    return all_html


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
