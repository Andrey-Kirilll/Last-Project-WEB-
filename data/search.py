import pygame
import requests
import sys
import os


def show_map(ll_spn=None, map_type="map", add_params=None, size=(600, 450)):
    if ll_spn:
        map_request = f"http://static-maps.yandex.ru/1.x/?{ll_spn}&l={map_type}"
    else:
        map_request = f"http://static-maps.yandex.ru/1.x/?l={map_type}"

    if add_params:
        map_request += "&" + add_params
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Запишем полученное изображение в файл.
    map_file = 'static/img/map.png'
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
        file.close()
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

    return map_file

    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode(size)
    # Рисуем картинку, загружаемую из только что созданного файла.
    screen.blit(pygame.image.load(map_file), (0, 0))
    # Переключаем экран и ждем закрытия окна.
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pass

    pygame.quit()
    # Удаляем за собой файл с изображением.
    os.remove(map_file)


def find_businesses(ll, spn, request, locale="ru_RU"):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"  # вставить api_key
    search_params = {
        "apikey": api_key,
        "text": request,
        "lang": locale,
        "ll": ll,
        "spn": spn,
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
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


API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'


def geocode(address):
    # Собираем запрос для геокодера.
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"}

    # Выполняем запрос.
    response = requests.get(geocoder_request, params=geocoder_params)

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
        return (None, None)

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
    address_ll = f"{lat},{lon}"

    # Подбираем масштаб, чтобы получить минимум count организаций.
    delta = 0.001
    organizations = []
    while delta < 100 and len(organizations) < count:
        delta *= 2.0
        span = f"{delta},{delta}"
        organizations = find_businesses(address_ll, span, organ)

    # Формируем список из координат организаций и их круглосуточности
    organs_with_time = []
    for org in organizations:
        point = org["geometry"]["coordinates"]
        hours = org["properties"]["CompanyMetaData"].get("Hours", None)
        if hours:  # У организации есть данные о времени работы
            available = hours["Availabilities"][0]
            is_24x7 = available.get("Everyday", False) and available.get("TwentyFourHours", False)
        else:  # Данных о времени работы нет.
            is_24x7 = None
        # Запоминаем полученные данные.
        organs_with_time.append((point, is_24x7))

    # Формируем параметр с точками
    points_param = "pt=" + "~".join([
        f'{point[0]},{point[1]},pm2{"gn" if is_24x7 else ("lb" if not is_24x7 else "gr")}l'
        for point, is_24x7 in organs_with_time])

    # Используем автопозиционирование карты по всем меткам.
    return show_map(map_type="map", add_params=points_param)


if __name__ == "__main__":
    main('магнит', 'Псков Рокоссовского 34', 2)
