import requests
import json
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
token_yandex_geo = config.get('default','token_yandex_geo') # API токен Яндекс геокодера

def geocoder(request):    
    results = 3  # Число кратное 3
    url_yandex = f'https://geocode-maps.yandex.ru/1.x/?apikey={token_yandex_geo}&geocode={request}&results={results}&format=json&lang=ru_RU'
    req_yan = requests.get(url=url_yandex)
    if req_yan.status_code == 200:
        data_req_yan = json.loads(req_yan.text)
        latitude = []
        longitude = []
        city = []
        message = []

        for i in range(results):    
            res = data_req_yan['response']['GeoObjectCollection']['featureMember'][i]['GeoObject']['Point']['pos']
            parts = res.split()
            latitude.append(float(parts[0]))
            longitude.append(float(parts[1]))
            city.append(data_req_yan['response']['GeoObjectCollection']['featureMember'][i]['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']) 
            message.append(f'''➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖
{city[i]}
Формат координат: WGS84 градусы
Широта: {latitude[i]}° Долгота: {longitude[i]}°
''')
        
        # Разбиваем сообщения на части
        message_parts = ["".join(message[i:i+3]) for i in range(0, len(message), 3)]

        # Возвращаем сообщения вместе с HTTP-статусом
        return req_yan.status_code, message_parts
    else:
        # В случае ошибки возвращаем только HTTP-статус
        return req_yan.status_code