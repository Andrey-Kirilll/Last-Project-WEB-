from requests import get
from sys import exit
import os


def show_map(ll_spn=None, map_type="map", add_params=None, orgs_addresses=None):
    if ll_spn:
        map_request = f"http://static-maps.yandex.ru/1.x/?{ll_spn}&l={map_type}"
    else:
        map_request = f"http://static-maps.yandex.ru/1.x/?l={map_type}"

    if add_params:
        map_request += "&" + add_params
    response = get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        exit(1)

    # Запишем полученное изображение в файл, предварительно удалив.
    n = None
    files = os.listdir(path="static/img")
    for i in files:
        if i.startswith('map') and i.endswith('.png'):
            n = int(i[i.index('p') + 1: i.index('.')])
            map_file = f'static/img/map{n}.png'
            #if os.path.exists(map_file):
                #os.remove(map_file.replace('/', '\\'))
    if n is None:
        n = 0
    if n < 1000:
        new_n = n + 1
    else:
        new_n = 1
    new_map_file = f'static/img/map{new_n}.png'
    try:
        with open(new_map_file, "wb") as file:
            file.write(response.content)
        file.close()
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        exit(2)

    return orgs_addresses, new_n


def find_businesses(ll, spn, request, locale="ru_RU"):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    search_params = {
        "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
        "text": request,
        "lang": locale,
        "ll": ll,
        "spn": spn,
        "type": "biz"
    }

    response = get(search_api_server, params=search_params)
    if not response:
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {search_api_server}
            Http статус: {response.status_code} ({response.reason})""")

    # Преобразуем ответ в json-объект
    json_response = response.json()

    # Получаем первую найденную организацию.
    organizations = json_response["features"]
    return organizations


def geocode(address):
    # Собираем запрос для геокодера.
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": '40d1649f-0493-4b70-98ba-98533de7710b',
        "geocode": address,
        "format": "json"}

    # Выполняем запрос.
    response = get(geocoder_request, params=geocoder_params)

    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
    else:
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {geocoder_request}
            Http статус: {response.status_code} ({response.reason})""")

    # Получаем первый топоним из ответа геокодера.
    # Согласно описанию ответа он находится по следующему пути:
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"] if features else None


# Получаем координаты объекта по его адресу.
def get_coordinates(address):
    toponym = geocode(address)
    if not toponym:
        return None, None

    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Широта, преобразованная в плавающее число:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return float(toponym_longitude), float(toponym_lattitude)


# Получаем параметры объекта для рисования карты вокруг него.
def get_ll_span(address):
    toponym = geocode(address)
    if not toponym:
        return None, None

    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и Широта :
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    # Собираем координаты в параметр ll
    ll = ",".join([toponym_longitude, toponym_lattitude])

    # Рамка вокруг объекта:
    envelope = toponym["boundedBy"]["Envelope"]

    # левая, нижняя, правая и верхняя границы из координат углов:
    l, b = envelope["lowerCorner"].split(" ")
    r, t = envelope["upperCorner"].split(" ")

    # Вычисляем полуразмеры по вертикали и горизонтали
    dx = abs(float(l) - float(r)) / 2.0
    dy = abs(float(t) - float(b)) / 2.0

    # Собираем размеры в параметр span
    span = f"{dx},{dy}"

    return ll, span


def find_business(ll, spn, request, locale="ru_RU"):
    orgs = find_businesses(ll, spn, request, locale=locale)
    if len(orgs):
        return orgs[0]


def main(organ, address, count):
    toponym_to_find = address

    if not toponym_to_find:
        print('No data')
        exit(1)

    lat, lon = get_coordinates(toponym_to_find)
    if lat is None or lon is None:
        return None, None
    address_ll = f"{lat},{lon}"

    # Подбираем масштаб, чтобы получить минимум count организаций.
    delta = 0.01
    organizations = []
    while delta < 100 and len(organizations) < count:
        delta *= 2.0
        span = f"{delta},{delta}"
        organizations = find_businesses(address_ll, span, organ)

    # Формируем список из координат организаций и их круглосуточности
    organs_with_time = []
    orgs_addresses = []
    n = 1
    for org in organizations:
        point = org["geometry"]["coordinates"]
        hours = org["properties"]["CompanyMetaData"].get("Hours", None)
        org_address = org["properties"]["description"]
        if hours:  # У организации есть данные о времени работы
            available = hours["Availabilities"][0]
            is_24x7 = available.get("Everyday", False) and available.get("TwentyFourHours", False)
        else:  # Данных о времени работы нет.
            is_24x7 = None
        # Запоминаем полученные данные.
        organs_with_time.append((point, is_24x7, n))
        orgs_addresses.append(org_address)
        n += 1

    # Формируем параметр с точками
    points_param = "pt=" + "~".join([
        f'{point[0]},{point[1]},pm2{"gn" if is_24x7 else ("lb" if not is_24x7 else "gr")}m{number}'
        for point, is_24x7, number in organs_with_time])

    # Используем автопозиционирование карты по всем меткам.
    return show_map(map_type="map", add_params=points_param, orgs_addresses=orgs_addresses)


if __name__ == "__main__":
    main('магнит', 'Псков Рокоссовского 34', 2)
