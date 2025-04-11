import requests
import json
import html2text
import configparser
import re

config = configparser.ConfigParser()
config.read('config.ini')
token_yandex_geo = config.get('default', 'token_yandex_geo')  # API токен Яндекс геокодера
admin_id = int(config.get('default', 'admin_id'))  # id админа


def wgs84_to_sk42(message):
    pattern = r"\d{2,3}\.\d{5,14}"
    numbers = re.findall(pattern, message)
    if len(numbers) == 2:
        try:
            latitude = float(numbers[0])
            longitude = float(numbers[1])
            url = f"https://sk42.org/ru/?direction=toSK42&convstr={latitude}°%E2%80%AFN+{longitude}°%E2%80%AFE"
            response = requests.get(url)
            if response.status_code == 200:
                text_content = html2text.html2text(response.text)
                x_pos = text_content.find("X:")
                y_pos = text_content.find("Y:")
                if x_pos != -1 and y_pos != -1:
                    try:
                        x_value = int(text_content[x_pos + 2:x_pos + 14].strip().replace("|", "").strip())
                        y_value = int(text_content[y_pos + 2:y_pos + 14].strip().replace("|", "").strip())
                        return x_value, y_value, latitude, longitude
                    except:
                        return f"Ошибка"
                else:
                    return f"Ошибка"
            else:
                return f"Ошибка сервера: {response.status_code}"
        except:
            return f"Некорректный формат"
    else:
        return f"Некорректный формат"


def sk42_to_wgs84(message):
    pattern = r"\b\d{5,8}\b"
    numbers = re.findall(pattern, message)
    if len(numbers) == 2:
        try:
            x = int(numbers[0])
            y = int(numbers[1])
            url = f"https://sk42.org/ru/?direction=fromSK42&convstr=X%E2%80%AF%3D%E2%80%AF{x}++Y%E2%80%AF%3D%E2%80%AF{y}"
            response = requests.get(url)
            if response.status_code == 200:
                text_content = html2text.html2text(response.text)
                n_pos = text_content.find("широта:")
                e_pos = text_content.find("долгота:")
                if n_pos != -1 and e_pos != -1:
                    try:
                        n_value = round(float(text_content[n_pos + 8:n_pos + 27].strip().replace("|", "").strip()), 6)
                        e_value = round(float(text_content[e_pos + 9:e_pos + 29].strip().replace("|", "").strip()), 6)
                        return n_value, e_value, x, y
                    except:
                        return f"Ошибка"
                else:
                    return f"Ошибка"
            else:
                return f"Ошибка сервера: {response.status_code}"
        except:
            return f"Некорректный формат"
    else:
        return f"Некорректный формат"


def geocoder(request):
    results = 3  # Число кратное 3
    url_yandex = f'https://geocode-maps.yandex.ru/1.x/?apikey={token_yandex_geo}&geocode={request}&results={results}&format=json&lang=ru_RU'
    req_yan = requests.get(url=url_yandex)
    if req_yan.status_code == 200:
        data_req_yan = json.loads(req_yan.text)
        found = int(
            data_req_yan['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found'])
        latitude = []
        longitude = []
        city = []
        message = []
        if found == 0:
            return req_yan.status_code, "Некорректное название, попробуйте ещё раз /search"
        for i in range(found):
            res = data_req_yan['response']['GeoObjectCollection']['featureMember'][i]['GeoObject']['Point']['pos']
            parts = res.split()
            latitude.append(float(parts[1]))
            longitude.append(float(parts[0]))
            city.append(
                data_req_yan['response']['GeoObjectCollection']['featureMember'][i]['GeoObject']['metaDataProperty'][
                    'GeocoderMetaData']['text'])
            message.append(f'''➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖
{city[i]}
Формат координат: WGS84 градусы
N: {latitude[i]}° E: {longitude[i]}°
''')

        # Разбиваем сообщения на части
        message_parts = ["".join(message[i:i + 3]) for i in range(0, len(message), 3)]

        # Возвращаем сообщения вместе с HTTP-статусом
        return req_yan.status_code, message_parts
    else:
        # В случае ошибки возвращаем только HTTP-статус
        return req_yan.status_code


def notification(message):
    # Замена None в userdata на ""
    message.chat.username = message.chat.username if message.chat.username else ""
    message.chat.first_name = message.chat.first_name if message.chat.first_name else ""
    message.chat.last_name = message.chat.last_name if message.chat.last_name else ""
    # Уведомление админа о запуске бота
    if message.chat.id != admin_id:
        return f"Пользователь @{message.chat.username} {message.chat.first_name} {message.chat.last_name} написал в бота {message.text}"
    else:
        return None
