#! /usr/bin/env python
# ver2
# -*- coding: utf-8 -*-

import logging
import telebot
import configparser
import db
import functions
from commands import *

# Настройка логирования
logging.basicConfig(filename='error_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

config = configparser.ConfigParser()
config.read('config.ini')
bot_api_token = config.get('default', 'bot_api_token')
bot = telebot.TeleBot(bot_api_token)
admin_id = int(config.get('default', 'admin_id'))  # id админа

db.create_table('users',
                ['id INTEGER PRIMARY KEY', 'username TEXT', 'firstname TEXT', 'lastname TEXT', 'requests INTEGER'])
db.create_table('buttons',
                ['id INTEGER PRIMARY KEY'] + [f'name{i} TEXT, latitude{i} INTEGER, longitude{i} INTEGER' for i in
                                              range(1, 6)])


def update_user_data(chat_id, username, first_name, last_name):
    try:
        db.update_user_data(chat_id, username, first_name, last_name)
    except Exception as e:
        logging.error(f"Error updating user data: {e}")


def send_notification(admin_id, notification):
    try:
        if notification:
            bot.send_message(admin_id, notification)
    except Exception as e:
        logging.error(f"Error sending notification: {e}")


@bot.message_handler(commands=['wgs84_to_sk42', 'sk42_to_wgs84', 'start', 'errors', 'me', 'add', 'delete', 'search'])
def handle_command(message):
    if str(message.chat.id)[0:1] != "-":
        try:
            command_parts = message.text.split()
            command = command_parts[0][1:]
            update_user_data(message.chat.id, message.chat.username, message.chat.first_name, message.chat.last_name)
            notification = functions.notification(message)
            send_notification(admin_id, notification)

            if command == 'wgs84_to_sk42':
                wgs84_to_sk42(message, bot)
            elif command == 'sk42_to_wgs84':
                sk42_to_wgs84(message, bot)
            elif command == 'start':
                start(message, bot)
            elif command == 'errors':
                errors(message, bot)
            elif command == 'me':
                me(message, bot)
            elif command == 'add':
                add_location_command(message, bot)
            elif command == 'delete':
                delete_button(message, bot)
            elif command == 'search':
                search(message, bot)

        except Exception as e:
            logging.error(f"Error handling command: {e}")


# Обработчик получения погоды из кнопки или местоположения
@bot.message_handler(content_types=['text', 'location'])
def handle_get_weather(message):
    if str(message.chat.id)[0:1] != "-":
        try:
            get_weather(message, bot)
            update_user_data(message.chat.id, message.chat.username, message.chat.first_name, message.chat.last_name)
            notification = functions.notification(message)
            send_notification(admin_id, notification)

        except Exception as e:
            logging.error(f"Error handling get_weather: {e}")


# Запустить бот
bot.polling(none_stop=True)