# Telegram Weather Bot 🌦️

Бот для Telegram, который показывает погоду по запросу пользователя.  
Работает круглосуточно на выделенном сервере. Используется `TeleBot` + автообновление через GitHub Actions.

---

## 🚀 Возможности

- Получение прогноза погоды по имени города
- Автоматическое обновление с GitHub при коммитах (`CI/CD`)
- Удобная архитектура для масштабирования
- Поддержка локальной базы SQLite

---

## 🛠️ Используемые технологии

- Python 3.9+
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)
- requests, configparser, Pillow и др.
- GitHub Actions для автоматического деплоя

---

## ⚙️ Установка и запуск

1. Клонируй репозиторий:

```bash
git clone https://github.com/MiheyKovalenko/telegram-weather-bot.git
cd telegram-weather-bot
```

2. Установи зависимости:

```bash
pip install -r requirements.txt
```

3. Добавь файл `config.ini`:

```ini
[default]
bot_api_token = ТВОЙ_ТОКЕН
admin_id = ТВОЙ_АЙДИ
token_yandex_geo = ТОКЕН_ЯНДЕКСА
```

4. Запусти бота:

```bash
python main.py
```

---

## ✅ Автодеплой

Проект использует GitHub Actions для автоматического обновления кода на сервере и перезапуска бота после каждого `git push`.

![Deploy status](https://github.com/MiheyKovalenko/telegram-weather-bot/actions/workflows/deploy.yml/badge.svg)

---

## 🤝 Контакты

Автор: [Mihey Kovalenko](https://github.com/MiheyKovalenko)  
Telegram: [@Miheyyka](https://t.me/Miheyyka)  

---

## 🧡 Поддержать

Если тебе понравилось — ⭐ поставь звезду репозиторию! Это мотивирует развивать проект :)
