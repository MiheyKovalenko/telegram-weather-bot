    Телеграм-бот для получения метео данных (температура, давление, направление и скорость ветра). 
    Для получения данных о погоде используются сервисы api.weather.yandex.ru/v2 и
    api.openweathermap.org, поэтому для работы бота нужны API токены этих сервисов. У Яндекс API
    ограничение на 50 запросов в сутки (бесплатный тариф), что должно хватить для небольшого проекта.

    Бота писал для локального использования. Жду предложений по улучшению кода.
    
    Команды для @BotFather
    start - ❔Помощь, запустить бота
    me - 👤Профиль
    add - ❇️Добавить локацию
    delete - ⛔️Удалить локацию
    search - 🔍Поиск координат по названию

    Файл config.ini:
    [default]
    bot_api_token = 9999999:skci8fkk-kdif8f8riei8c8cid
    token_openweathermap = id89oejd8f8r8ieid8c8d8riri8f8f
    token_yandex_geo = x9x9x9x9-x9x9-x9x9-x9x9-x9x9x9x9x9x9
    admin_id = 9999999

    [token_yandex]
    1 = x9x9x9x9-x9x9-x9x9-x9x9-x9x9x9x9x9x9
    2 = x9x9x9x9-x9x9-x9x9-x9x9-x9x9x9x9x9x9