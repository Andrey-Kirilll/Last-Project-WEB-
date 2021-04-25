from requests import put
from pprint import pprint

url = 'http://127.0.0.1:5000'
token = 'yandex_lyceum_project'
login = 'x@a'

pprint(put(f'{url}/api/upt_account/1&login={login}&token={token}', json={}).json())

pprint(put(f'{url}/api/upt_account/1&login={login}&token={token}', json={'': ''}).json())

pprint(put(f'{url}/api/upt_account/634578679895&login={login}&token={token}', json={"email": ''}).json())

pprint(put(f'{url}/api/upt_account/7&login={login}&token={token}', json={'email': 'as@k', "name": 'star'}).json())

pprint(put(f'{url}/api/upt_account/7&login={login}&token={token}', json={'store_address': ''}).json())

pprint(put(f'{url}/api/upt_account/3&login={login}&token={token}', json={'store_address': 'апц, пакцуа, 23'}).json())

pprint(put(f'{url}/api/upt_account/3&login={login}&token={token}',
           json={'store_address': 'апц, пакцуа, 23', 'store_name': 'Пятёрочка'}).json())

pprint(put(f'{url}/api/upt_account/3&login={login}&token={token}', json={'store_name': 'Пятёрочка'}).json())
