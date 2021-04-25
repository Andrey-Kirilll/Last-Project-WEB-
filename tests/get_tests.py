from pprint import pprint
from requests import get

url = 'http://127.0.0.1:5000'
token = 'yandex_lyceum_project'
login = 'x@a'

pprint(get(f'{url}/api/get_all_accounts&login={login}&token=greferfwe').json())

pprint(get(f'{url}/api/get_all_accounts&login={login}&token={token}').json())

pprint(get(f'{url}/api/get_one_account/4&login={login}&token={token}').json())

pprint(get(f'{url}/api/get_one_account/2&login={login}&token={token}').json())

pprint(get(f'{url}/api/get_one_account/3&login={login}&token={token}').json())

pprint(get(f'{url}/api/get_one_account/2&login={login}&token=yandexпукауt').json())
