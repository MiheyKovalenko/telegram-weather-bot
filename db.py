import sqlite3

def create_table(table_name, columns): # Общая функция для создания таблиц
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    columns_str = ', '.join(columns)
    query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})'
    
    cursor.execute(query)
    conn.commit()
    
    cursor.close()
    conn.close()

def get_requests(id): # Получаем кол-во запросов пользователя
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    cursor.execute('''SELECT requests FROM users WHERE id = ?''', (id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def update_requests(id, new_requests): # Обновляем кол-во запросов пользователя
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET requests = ? WHERE id = ?''', (new_requests, id))
    conn.commit()
    cursor.close()
    conn.close()

def update_user_data(user_id, username, firstname, lastname):
    # Устанавливаем соединение с базой данных
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Проверяем, есть ли пользователь с таким идентификатором в базе данных
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    
    if user:
        # Если пользователь существует, обновляем его данные
        cursor.execute("UPDATE users SET username=?, firstname=?, lastname=? WHERE id=?", (username, firstname, lastname, user_id))
    else:
        # Иначе создаём нового пользователя 
        requests = 0
        cursor.execute('''INSERT INTO users(id, username, firstname, lastname, requests) 
                          VALUES(?, ?, ?, ?, ?)''', (user_id, username, firstname, lastname, requests))
    
    conn.commit()
    # Закрываем соединение с базой данных
    cursor.close()
    conn.close()

def get_buttons(user_id):
    # Устанавливаем соединение с базой данных
    conn = sqlite3.connect('bot.db')
    # Создаем объект-курсор для выполнения SQL-запросов
    cursor = conn.cursor()
    
    # Проверяем, есть ли пользователь с таким идентификатором в базе данных
    query = "SELECT * FROM buttons WHERE id=?"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    
    if result:
        # Если пользователь существует, возвращаем результат поиска
        return result[1:16]
    else:
        # Иначе создаем нового пользователя в базе данных
        query = "INSERT INTO buttons(id) VALUES(?)"
        cursor.execute(query, (user_id,))
        # Сохраняем изменения
        conn.commit()
        return None
    # Закрываем курсор и соединение с базой данных
    cursor.close()
    conn.close()

# Function to delete a button by name
def delete_button_by_name(user_id, button_name):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    # Retrieve the current button data for the user
    cursor.execute("SELECT * FROM buttons WHERE id=?", (user_id,))
    result = cursor.fetchone()
    result = result[1:16]
    if result:
        # Iterate through the button names and check if any match the provided name
        for i in range(5):
            if result[i * 3] == button_name:
                # If a match is found, set the name, latitude, and longitude to None
                cursor.execute(f"UPDATE buttons SET name{i+1}=NULL, latitude{i+1}=NULL, longitude{i+1}=NULL WHERE id=?", (user_id,))
                conn.commit()
                cursor.close()
                conn.close()
                return f"Локация '{button_name}' удалена."
    
    cursor.close()
    conn.close()
    return f"Локация '{button_name}' не найдена.\nВыполните команду /start"

# Function to add a location to the buttons table
def add_location(user_id, location_name, latitude, longitude):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()

    # Retrieve the current button data for the user
    cursor.execute("SELECT * FROM buttons WHERE id=?", (user_id,))
    result = cursor.fetchone()
    result = result[1:16]
    if result:
        # Iterate through the button names and find the first empty slot
        for i in range(5):
            if result[i * 3] is None:
                cursor.execute(f"UPDATE buttons SET name{i+1}=?, latitude{i+1}=?, longitude{i+1}=? WHERE id=?", (location_name, latitude, longitude, user_id))
                conn.commit()
                cursor.close()
                conn.close()
                return f"Локация '{location_name}' N: {latitude}° E: {longitude}° добавлена. Выполните команду /start."

    cursor.close()
    conn.close()
    return "Нет свободной кнопки для локации. Вы можете удалить локацию командой /delete."
