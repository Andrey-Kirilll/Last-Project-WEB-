from requests import delete
from pprint import pprint

url = 'http://127.0.0.1:5000'
token = 'yandex_lyceum_project'
login = 'x@a'

pprint(delete(f'{url}/api/del_account/4&login=fewg@a&token={token}').json())

pprint(delete(f'{url}/api/del_account/4&login={login}&token={token}').json())

pprint(delete(f'{url}/api/del_account/6&login={login}&token={token}').json())
