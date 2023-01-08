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
    html_ = "var data = []; \n"
    asset_name = None
    for asset_h in data:
        if asset_name is None:
            asset_name = asset_h['display_name']
        html_ = html_+"data.push({ '"+ asset_h['display_name']+"': '"+str(int(asset_h['price_lovelace'])//1000000)+"'}); \n"

    html_template = open("template.html", "rt")
    html_graph = html_template.read()
    
    html_graph = html_graph.replace('#PUSH_DATA#', html_)
    html_graph = html_graph.replace('#DISPLAY_NAME#', asset_name)
    html_template.close()
    return html_graph

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8080)
