import json
from flask_login import current_user
from . import db_session
from .models import Resources, People


def form_basket(addresses):
    with open('static/json/stores.json', 'r') as f:
        data = json.load(f)

        done_addresses = []
        labels = ['ул.', 'просп.', 'д.']
        for item in addresses:
            address = item.split(', ')[:-1]
            for label in labels:
                if label in address[0]:
                    address[0] = address[0].replace(label, '').strip()
                elif label in address[1]:
                    address[1] = address[1].replace(label, '').strip()
                elif label in address[2]:
                    address[2] = address[2].replace(label, '').strip()
            for i in range(len(address)):
                address[i] = address[i].lower()
            done_addresses.append(address)

        store_adrs = []
        for store in data:
            store_adr = store['address'].lower().split(', ')
            store_adrs.append(store_adr)

        new_data = []
        for i in range(len(done_addresses)):
            item = done_addresses[i]
            adr = [item[2], item[0], item[1]]
            print(adr)
            if adr in store_adrs:
                n = store_adrs.index(adr)
                tmp = data[n]
                tmp['number'] = i + 1
                new_data.append(tmp)
            else:  # пока заглушка, в дальнейшем это будет подгрузка стандартного ассортимента данной организации
                tmp = data[0]
                tmp['number'] = i + 1
                new_data.append(tmp)

        return new_data


db_session.global_init("db/search_system.db")  # инициилизация дб
db_sess = db_session.create_session()
store_adr = ''  # Адрес магазина, где мы ищем товары
data = [x.store_basket for x in db_sess.query(Resources).filter_by(store_address=store_adr).all()]
print(data)


work = [x.serialize for x in db_sess.query(People).filter_by(id=2).all()]
print(work)
