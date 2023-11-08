#! /usr/bin/env python
# ver2
# -*- coding: utf-8 -*-

import telebot
from telebot import types
import requests
import json
import configparser
import db
from commands import *

config = configparser.ConfigParser()
config.read('config.ini')
bot_api_token = config.get('default','bot_api_token') # Токен API телеграм бота
bot = telebot.TeleBot(bot_api_token)

db.create_table_users()
db.create_table_buttons()

# Команда старт
@bot.message_handler(commands=['start'])
def handle_start(message):
    start(message, bot)

# Команда получения профиля
@bot.message_handler(commands=['me'])
def handle_me(message):
    me(message, bot)

# Команда добавления локации
@bot.message_handler(commands=['add'])
def handle_add_location_command(message):
    add_location_command(message, bot)
# Получаем имя локации
def process_add_location_name(message):
    add_location_name(message, bot)
# Получаем координаты локации и добавляем в базу
def process_add_location_latitude(message, location_name):
    add_location_latitude(message, location_name, bot)
def process_add_location_longitude(message, location_name, latitude):
    add_location_name_longitude(message, location_name, latitude, bot)

# Команда удаления кнопки
@bot.message_handler(commands=['delete'])
def handle_delete_button(message):
    delete_button(message, bot)
# Процесс удаления кнопки
def handle_process_delete_button(message):
    process_delete_button(message, bot)

# Команда поиска координат локации
@bot.message_handler(commands=['search'])
def handle_search(message):
    search(message, bot)
# Ответ
def handle_request(message):
    request(message, bot)
    
# Обработчик получения погоды из кнопки или местоположения
@bot.message_handler(content_types=['text', 'location'])
def handle_get_weather(message):
    get_weather(message, bot)

# Запустить бот
bot.polling(none_stop=True)