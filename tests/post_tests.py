from pprint import pprint
from requests import post

url = 'http://127.0.0.1:5000'
token = 'yandex_lyceum_project'
login = 'x@a'

pprint(post(f'{url}/api/add_account').json())

pprint(post(f'{url}/api/add_account/user').json())

pprint(post(f'{url}/api/add_account/user&login={login}&token={token}').json())

pprint(post(f'{url}/api/add_account/user&login={login}&token={token}',
            json={'surname': 'Киселёв',
                  'name': 'Иван',
                  'email': 'jyt@ru',
                  'password': '34'}).json())

pprint(post(f'{url}/api/add_account/admin&login={login}&token={token}',
            json={'title': 'Заголовок',
                  'content': 'Текст новости',
                  'user_id': 1,
                  'is_private': False}).json())
