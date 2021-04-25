from . import db_session
from .models import Resources


def modify_adr(adr):
    city, street, house = adr.split(', ')
    city, street, house = city.capitalize(), street.capitalize(), house.upper()
    return ', '.join([city, street, house])


def form_basket(addresses, store_name):
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
    for i in range(len(done_addresses)):
        item = done_addresses[i]
        adr = [item[2], item[0], item[1]]
        store_adrs.append(', '.join(adr))

    store_baskets = []
    db_session.global_init("db/search_system.db")  # инициилизация дб
    db_sess = db_session.create_session()
    n = 0
    for store_adr in store_adrs:  # Адрес магазина, где мы ищем товары
        n += 1  # Обновляем номер отметки на карте
        db = db_sess.query(Resources).filter_by(store_address=store_adr).all()
        basket = dict()
        if db:
            for i in range(len(db)):
                item = db[i].store_basket
                if item['store'] == store_name:
                    if not basket:
                        basket = {'store': item['store'], 'address': modify_adr(item['address']), 'number': str(n),
                                  'items': {
                                      f'{item["type"]}': [[item['name'], item['price'], item['count']]]
                                  }}
                    else:
                        if item['type'] in basket['items']:
                            basket['items'][item['type']].append([item['name'], item['price'], item['count']])
                        else:
                            basket['items'][item['type']] = [[item['name'], item['price'], item['count']]]
        else:
            basket = {
                'number': str(n),
                'address': modify_adr(store_adr)
            }
        store_baskets.append(basket)
    return store_baskets
