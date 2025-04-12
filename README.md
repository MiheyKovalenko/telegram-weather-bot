# Telegram Weather Bot 🌦️

[![GitHub](https://img.shields.io/badge/GitHub-MiheyKovalenko-181717?logo=github)](https://github.com/MiheyKovalenko)
[![Telegram](https://img.shields.io/badge/Telegram-%40Miheyyka-2CA5E0?logo=telegram)](https://t.me/Miheyyka)
[![Bot](https://img.shields.io/badge/Бот-%40fp_weather_bot-2CA5E0?logo=telegram)](https://t.me/fp_weather_bot)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Deploy status](https://github.com/MiheyKovalenko/telegram-weather-bot/actions/workflows/deploy.yml/badge.svg)](https://github.com/MiheyKovalenko/telegram-weather-bot/actions)
[![Weather API](https://img.shields.io/badge/Data%20Source-Open--Meteo-blue?logo=cloud)](https://open-meteo.com/)
---

Бот для Telegram, который показывает погоду по запросу пользователя.  
Работает круглосуточно на выделенном сервере с автодеплоем через GitHub Actions. Написан на Python с использованием `pyTelegramBotAPI`.

---

## 🚀 Возможности

- Получение прогноза погоды по названию населённого пункта
- Поддержка автодеплоя через GitHub Actions
- Удобная архитектура: отдельные модули, логирование
- Ведение логов команд и ошибок
- Хранение пользовательских данных в SQLite

---

## 🛠️ Используемые технологии

- Python 3.9+
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI), requests, configparser, Pillow, html2text
- GitHub Actions (CI/CD)
- systemd (для автозапуска на сервере)

---

## 📡 Источник данных

Прогнозы погоды и геокодирование предоставлены [Open-Meteo.com](https://open-meteo.com/), лицензия [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

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

3. Добавь файл `config.ini` со своими ключами:

```ini
[default]
bot_api_token = ТВОЙ_ТОКЕН
admin_id = ТВОЙ_АЙДИ
```

4. Запусти бота:

```bash
python main.py
```

---

## 🧡 Поддержать

Если тебе понравилось — ⭐ поставь звезду репозиторию!  
Это мотивирует меня развивать проект дальше :)
