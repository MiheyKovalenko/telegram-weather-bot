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

admin_id = int(config.get('default', 'admin_id'))  # id админа


# Команда старт
def start(message: Message, bot: TeleBot):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button_data = db.get_buttons(message.chat.id)  # Получаем кнопки

    if button_data:
        buttons = []
        for i in range(5):
            name = button_data[i * 3]  # Получаем имена кнопок
            if name:
                buttons.append(types.KeyboardButton(name))

        markup.add(*buttons)  # Добавляем кнопки на клавиатуру
    bot.send_message(message.chat.id, f"""
Привет, {message.chat.first_name}!
Этот бот предоставляет различные функции для работы с локациями.
Вот список доступных команд:
❔Помощь, запустить бота /start
❗️Частые ошибки /errors
👤Профиль /me
❇️Добавить локацию /add
⛔️Удалить локацию /delete
🔍Поиск координат по названию /search
🔁Перевод из WGS84 в СК42
/wgs84_to_sk42
🔁Перевод из СК42 в WGS84
/sk42_to_wgs84
Вы также можете отправить местоположение вложением
Бот поддерживает 5 локаций
""", reply_markup=markup)


# Команда получения частых ошибок
def errors(message: Message, bot: TeleBot):
    bot.send_message(message.chat.id, f'''
❗️ОШИБКА
Ошибка преобразования координат, возможные причины: не верный формат координат, не удается определить мхезанизм преобразования EPSG для соответствующей зоны СК-42 ( отсутствует покрытие данного участка земной поверхности )

❔Как это работает:
Для преобразования координат используется метод ST_Transform() postgis. Преобразования координат доступны для територии стран бывшего СССР и прилегающих областей (там, где в основном использовалась СК-42) Неточность преобразования может достигать десятка метров (горные районы), обычно единицы метров.
''')


# Команда получения профиля
def me(message: Message, bot: TeleBot):
    text1 = f"👤Username: @{message.chat.username}\n" if message.chat.username else ""
    text2 = f"▪️Имя: {message.chat.first_name}\n" if message.chat.first_name else ""
    req = db.get_requests(message.chat.id)
    bot.send_message(message.chat.id, f'''
Ваш профиль:
🪪ID: {message.chat.id}
{text1}{text2}🌤Выполненных запросов погоды: {req}
''')


# Команда добавления локации
def add_location_command(message: Message, bot: TeleBot):
    bot.send_message(message.chat.id, "Отправьте название локации")
    bot.register_next_step_handler(message, process_add_location_name, bot=bot)


# Получаем имя локации
def process_add_location_name(message: Message, bot: TeleBot):
    if len(message.text) < 60:
        location_name = message.text
        bot.send_message(message.chat.id, f"""
Отправьте координаты локации
в формате WGS84 широта/долгота,
например N: 47.12345° E: 37.54321°
или СК42, например X: 654321 Y: 654321
""")
        bot.register_next_step_handler(message, process_add_location, location_name, bot=bot)
    else:
        bot.send_message(message.chat.id, "Отправьте корректное название локации (длина названия не больше 60)")
        bot.register_next_step_handler(message, process_add_location_name, bot=bot)


# Получаем координаты локации и добавляем в базу
def process_add_location(message: Message, location_name, bot: TeleBot):
    pattern = r"\d{2,3}\.\d{5,14}"
    numbers = re.findall(pattern, message.text)
    if len(numbers) == 2:
        latitude = round(float(numbers[0]), 6)
        longitude = round(float(numbers[1]), 6)
        result = db.add_location(message.chat.id, location_name, latitude, longitude)
        bot.send_message(message.chat.id, result)
    else:
        answer = functions.sk42_to_wgs84(message.text)
        if isinstance(answer, str):
            bot.send_message(message.chat.id, f"""
{answer}.\nПожалуйста отправьте ещё раз
в формате WGS84 широта/долгота,
например N: 47.12345° E: 37.54321°
или СК42, например X: 654321 Y: 654321
""")
            bot.register_next_step_handler(message, process_add_location, location_name, bot=bot)
        else:
            result = db.add_location(message.chat.id, location_name, answer[0], answer[1])
            if result[:9] == "Локация '":
                bot.send_message(message.chat.id,
                                 f"Локация '{location_name}' X: {answer[2]} Y: {answer[3]} добавлена. Выполните команду /start.")
            else:
                bot.send_message(message.chat.id, result)


# Команда удаления кнопки
def delete_button(message: Message, bot: TeleBot):
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


# Команда поиска координат локации
def search(message: Message, bot: TeleBot):
    bot.send_message(message.chat.id, "Отправьте название искомой локации")
    bot.register_next_step_handler(message, request, bot=bot)


# Ответ
def request(message: Message, bot: TeleBot):
    if message.text.isdigit():
        bot.send_message(message.chat.id, "Некорректное название, попробуйте ещё раз /search")
    else:
        res = functions.geocoder(message.text)
        print(res)
        if res[0] == 200:
            bot.send_message(message.chat.id, res[1])
        else:
            bot.send_message(message.chat.id, f"Ошибка {res}")
        if message.chat.id != admin_id:
            bot.send_message(admin_id, f'''
Пользователь @{message.chat.username} {message.chat.first_name} {message.chat.last_name} запросил поиск локации {message.text}
''')


# Команда перевода координат из WGS84 в СК42
def wgs84_to_sk42(message: Message, bot: TeleBot):
    bot.send_message(message.chat.id, "Отправьте координаты в формате WGS84, например 47.54321 37.12345")
    bot.register_next_step_handler(message, answer_sk42, bot=bot)


def answer_sk42(message: Message, bot: TeleBot):
    answer = functions.wgs84_to_sk42(message.text)

    if isinstance(answer, str):
        bot.send_message(message.chat.id, answer)
    else:
        bot.send_message(message.chat.id, f"""
Данные координаты в WGS84:\nN: {answer[2]}° E: {answer[3]}°
Переведенные координаты в СК42:\nX: {answer[0]} Y: {answer[1]}
""")


# Команда перевода координат из СК42 в WGS84
def sk42_to_wgs84(message: Message, bot: TeleBot):
    bot.send_message(message.chat.id, "Отправьте координаты в формате СК42, например X = 654321  Y = 7654321")
    bot.register_next_step_handler(message, answer_wgs84, bot=bot)


def answer_wgs84(message: Message, bot: TeleBot):
    answer = functions.sk42_to_wgs84(message.text)
    if isinstance(answer, str):
        bot.send_message(message.chat.id, answer)
    else:
        bot.send_message(message.chat.id, f"""
Данные координаты в СК42:\nX: {answer[2]} Y: {answer[3]}
Переведенные координаты в WGS84:\nN: {answer[0]}° E: {answer[1]}°
""")


# Обработчик получения погоды из кнопки или местоположения
def get_weather(message: Message, bot: TeleBot):
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
        url_open_meteo = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m&wind_speed_unit=ms&timezone=Europe%2FMoscow"
        req_opmt = requests.get(url=url_open_meteo)

        if req_opmt.status_code == 200:
            data_req_opmt = json.loads(req_opmt.text)
            wind_60 = round(data_req_opmt["current"]["wind_direction_10m"] / 6, 2)
            wind_60 = '{:.2f}'.format(wind_60).replace('.', '-')
            bot.send_message(message.chat.id, f'''
По данным погоды в {location_name}:
Температура {data_req_opmt["current"]["temperature_2m"]} °С
Давление {int(round((data_req_opmt["current"]["surface_pressure"] * 0.75), 0))} мм рт. ст.
Направление ветра {data_req_opmt["current"]["wind_direction_10m"]}° ({wind_60})
Скорость ветра {round(data_req_opmt["current"]["wind_speed_10m"], 1)} м/с 
Порывы ветра {round(data_req_opmt["current"]["wind_gusts_10m"], 1)} м/с
''')

        elif req_opmt.status_code != 200:
            bot.send_message(admin_id,
                             f'Проблема с API у @{message.chat.username} {message.chat.first_name} {message.chat.last_name}\nCode: {req_opmt.status_code}')
            bot.send_message(message.chat.id, "Неполадки с ботом, напишите администратору")

        with open(r'log.txt', mode='a') as log:
            log.write(
                f'Пользователь @{message.chat.username} {message.chat.first_name} {message.chat.last_name} запросил погоду в {location_name}\n')
    else:
        bot.send_message(message.chat.id, 'Такой локации нет, добавьте с помощью команды /add')
