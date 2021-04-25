from requests import delete
from pprint import pprint

url = 'https://lastproject45234.herokuapp.com/'
token = 'yandex_lyceum_project'
login = 'x@a'

pprint(delete(f'{url}/api/del_account/4&login=fewg@a&token={token}').json())

pprint(delete(f'{url}/api/del_account/4&login={login}&token={token}').json())

pprint(delete(f'{url}/api/del_account/6&login={login}&token={token}').json())
