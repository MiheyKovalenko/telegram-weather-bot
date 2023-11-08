import configparser
import db
import functions
import requests
import json
import re
import time
from telebot import types, TeleBot
from telebot.types import Message

config = configparser.ConfigParser()
config.read('config.ini')

token_openweathermap = config.get('default','token_openweathermap') # API токен OpenWeatherMap
admin_id = int(config.get('default','admin_id')) # id админа

# Яндекс API токены
token_yandex_list = []
for key in config['token_yandex']:
    token_value = config['token_yandex'][key]
    token_yandex_list.append({'X-Yandex-API-Key': token_value})

code_to_smile = {
    "clear": "Ясно ☀️",
    "partly-cloudy": "Малооблачно 🌤",
    "overcast": "Пасмурно ☁️",
    "light-rain": "Небольшой дождь 🌦",
    "cloudy": "Облачно 🌥",
    "rain": "Дождь 🌧",
    "moderate-rain": "Умеренно сильный жождь 🌧",
    "heavy-rain": "Сильный дождь 🌧",
    "drizzle": "Дождь 🌧",
    "showers": "Ливень 🌧",
    "continuous-heavy-rain": "Длительный сильный дождь 🌧",
    "wet-snow": "Снег с дождем 🌨",
    "snow": "Снег 🌨",
    "light-snow": "Небольшой снег 🌨",
    "snow-showers": "Снегопад 🌨",
    "hail": "Град 🌧",
    "thunderstorm": "Гроза 🌩",
    "thunderstorm-with-rain": "Дождь с грозой ⛈",
    "thunderstorm-with-hail": "Гроза с градом ⛈",
}

# Команда старт
def start(message: Message, bot: TeleBot):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button_data = db.get_buttons(message.chat.id)  # Получаем кнопки
    db.update_user_data(message.chat.id, message.chat.username, message.chat.first_name, message.chat.last_name)

    if button_data:
        buttons = []
        for i in range(5):
            name = button_data[i * 3]  # Получаем имена кнопок
            if name:
                buttons.append(types.KeyboardButton(name))

        markup.add(*buttons)  # Добавляем кнопки на клавиатуру
    bot.send_message(message.chat.id, f"""
Привет, {message.chat.first_name}!
Отправьте местоположение вложением
Или добавьте локацию вручную
командой  /add
Бот поддерживает 5 локаций
Вы также можете удалить локацию
командой  /delete
""", reply_markup=markup)
    # Замена None в userdata на ""
    message.chat.username = message.chat.username if message.chat.username else ""
    message.chat.first_name = message.chat.first_name if message.chat.first_name else ""
    message.chat.last_name = message.chat.last_name if message.chat.last_name else ""
    # Уведомление админа о запуске бота
    if message.chat.id != admin_id:
        bot.send_message(admin_id, f"Пользователь @{message.chat.username} {message.chat.first_name} {message.chat.last_name} запустил бота.")

# Команда получения профиля
def me(message: Message, bot: TeleBot):
    db.update_user_data(message.chat.id, message.chat.username, message.chat.first_name,  message.chat.last_name)
    if message.chat.username == None:
        text1 = ""
        message.chat.username = ""
    else:
        text1 = f"👤Username: @{message.chat.username}\n"
    if message.chat.first_name == None:
        text2 = ""
        message.chat.first_name = ""
    else:
        text2 = f"▪️Имя: {message.chat.first_name}\n"
    req = db.get_requests(message.chat.id)
    bot.send_message(message.chat.id, f'''
Ваш профиль:
🪪ID: {message.chat.id}
{text1}{text2}🌤Выполненных запросов погоды: {req}
''')
    if message.chat.last_name == None:
        message.chat.last_name = ""
    if message.chat.id != admin_id:
        bot.send_message(admin_id, f'''
Пользователь @{message.chat.username} {message.chat.first_name} {message.chat.last_name} запросил профиль
''')

# Команда добавления локации
def add_location_command(message: Message, bot: TeleBot):
    bot.send_message(message.chat.id, "Отправьте название локации")
    bot.register_next_step_handler(message, process_add_location_name, bot=bot)
# Получаем имя локации
def process_add_location_name(message: Message, bot: TeleBot):
    location_name = message.text
    bot.send_message(message.chat.id, "Отправьте широту локации\n(координатная система WGS84 градусы, например 47.12345)")
    bot.register_next_step_handler(message, process_add_location_latitude, location_name, bot=bot)
# Получаем координаты локации и добавляем в базу
def process_add_location_latitude(message: Message, location_name, bot: TeleBot):
    latitude_input = message.text
    if re.match(r'^\d{2}\.\d+$', latitude_input):
        latitude = float(latitude_input)
        bot.send_message(message.chat.id, "Отправьте долготу локации\n(координатная система WGS84 градусы, например 37.54321)")
        bot.register_next_step_handler(message, process_add_location_longitude, location_name, latitude, bot=bot)
    else:
        bot.send_message(message.chat.id, "Некорректный формат широты\nПожалуйста отправьте ещё раз\n(координатная система WGS84 градусы, например 47.12345)")
        bot.register_next_step_handler(message, process_add_location_latitude, location_name, bot=bot)

def process_add_location_longitude(message: Message, location_name, latitude, bot: TeleBot):
    longitude_input = message.text
    if re.match(r'^\d{2}\.\d+$', longitude_input):
        longitude = float(longitude_input)
        result = db.add_location(message.chat.id, location_name, latitude, longitude)
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "Некорректный формат долготы\nПожалуйста отправьте ещё раз\n(координатная система WGS84 градусы, например 37.54321)")
        bot.register_next_step_handler(message, process_add_location_longitude, location_name, latitude, bot=bot)

# Команда удаления кнопки
def delete_button(message: Message, bot: TeleBot):
    db.update_user_data(message.chat.id, message.chat.username, message.chat.first_name, message.chat.last_name)
    bot.send_message(message.chat.id, "Выберите локацию для удаления.")
    bot.register_next_step_handler(message, process_delete_button, bot=bot)
# Процесс удаления кнопки
def process_delete_button(message: Message, bot: TeleBot):
    button_name = message.text
    result = db.delete_button_by_name(message.chat.id, button_name)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button_data = db.get_buttons(message.chat.id)
    if button_data:
        buttons = []
        for i in range(5):
            name = button_data[i * 3]
            if name:
                buttons.append(types.KeyboardButton(name))
        markup.add(*buttons)  
# Если кнопка удалена
    if f"Локация '{button_name}' не найдена.\nВыполните команду /start" in result:
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, result, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, result, reply_markup=markup)

# Команда поиска координат локации
def search(message: Message, bot: TeleBot):
    bot.send_message(message.chat.id, "Отправьте название искомой локации")
    bot.register_next_step_handler(message, request, bot=bot)
# Ответ
def request(message: Message, bot: TeleBot):
    try:
        int(message.text)
        bot.send_message(message.chat.id, "Некорректное название, попробуйте ещё раз /search")
    except ValueError:
        res = functions.geocoder(message.text)
        if res[0] == 200:
            sent_message = bot.send_message(message.chat.id, res[1])
        else:
            bot.send_message(message.chat.id, f"Ошибка {res}")
            
# Обработчик получения погоды из кнопки или местоположения
def get_weather(message: Message, bot: TeleBot):
    db.update_user_data(message.chat.id, message.chat.username, message.chat.first_name, message.chat.last_name)
    message.chat.username = message.chat.username if message.chat.username else ""
    message.chat.first_name = message.chat.first_name if message.chat.first_name else ""
    message.chat.last_name = message.chat.last_name if message.chat.last_name else ""
    location_name = message.text
    latitude = None
    longitude = None
    if message.location:
         latitude = str(message.location.latitude)[:8]
         longitude = str(message.location.longitude)[:8]
         
    # Проверка кнопки в базе
    button_data = db.get_buttons(message.chat.id)
    if button_data and message.location is None:
        for i in range(1, 6):
            name_column = button_data[i * 3 - 3]
            latitude_column = button_data[i * 3 - 2]
            longitude_column = button_data[i * 3 - 1]

            if name_column == location_name and latitude_column is not None and longitude_column is not None:
                latitude = latitude_column
                longitude = longitude_column
                break
                
    if latitude is not None and longitude is not None:
        new_requests = db.get_requests(message.chat.id) + 1
        db.update_requests(message.chat.id, new_requests)
        url_yandex = f'https://api.weather.yandex.ru/v2/informers?lat={latitude}&lon={longitude}&lang=ru_RU'
        url_openweathermap = f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={token_openweathermap}&exclude=current&units=metric'
        req_opwth = requests.get(url=url_openweathermap)
        if message.chat.id != admin_id:
            bot.send_message(admin_id, f'Пользователь @{message.chat.username} {message.chat.first_name} {message.chat.last_name} запросил погоду в {location_name}')
        for token in token_yandex_list:
            req_yan = requests.get(url=url_yandex, headers=token)
            if req_yan.status_code == 200 and req_opwth.status_code == 200:
                data_req_yan = json.loads(req_yan.text)
                data_req_opwth = json.loads(req_opwth.text)
                fact = data_req_yan["fact"]
                if fact["condition"] in code_to_smile:
                    wd = code_to_smile[fact["condition"]]
                    wd = wd.lower()
                else:
                    wd = "Творится что-то страшное!!!"
                wind_60 = round(data_req_opwth["wind"]["deg"] / 6, 2)
                wind_60 = '{:.2f}'.format(wind_60).replace('.', '-')
                bot.send_message(message.chat.id, f'''
По данным Яндекс Погоды 
в {location_name} {wd}
Температура {fact["temp"]}°С
Давление {fact["pressure_mm"]} мм рт. ст.
Направление ветра {data_req_opwth["wind"]["deg"]}° ({wind_60})
Скорость ветра {fact["wind_speed"]} м/с 
''')
                break
            elif req_yan.status_code != 200:
                bot.send_message(admin_id, f'Проблема с API у @{message.chat.username} {message.chat.first_name} {message.chat.last_name}\nYandex code: {req_yan.status_code}\nWeather code: {req_opwth.status_code}\nПодключаю запасной ключ API..')

        if req_yan.status_code != 200:
            bot.send_message(admin_id, "Всё трындец")
            bot.send_message(message.chat.id, "Неполадки с ботом, напишите администратору")
        
        with open(r'log.txt', mode='a') as log:
            log.write(f'Пользователь @{message.chat.username} {message.chat.first_name} {message.chat.last_name} запросил погоду в {location_name}\n')
    else:
        bot.send_message(message.chat.id, 'Такой локации нет')
        if message.chat.id != admin_id:
            bot.send_message(admin_id, f'Пользователь @{message.chat.username} {message.chat.first_name} {message.chat.last_name} написал в бот {message.text}')
            