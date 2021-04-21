import json


def form_basket():
    with open('static/json/stores.json', 'r') as f:
        data = json.load(f)
        return data
