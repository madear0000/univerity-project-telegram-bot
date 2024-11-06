import sqlite3
from datetime import datetime

# Подключение к базе данных
conn = sqlite3.connect("tasksForDoLater.db", check_same_thread=False)
cursor = conn.cursor()

# Создаем таблицу для хранения задач, если её еще нет
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        user_id INTEGER,
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT,
        difficulty INTEGER,
        reminder_date TEXT
    )
''')
conn.commit()

user_data = {}

def startLater(message, bot, types):
    if message.text == "📝 Задать новый график":
        bot.send_message(message.chat.id, "Хорошо, сколько задач вы хотите задать?", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, howManyTaskShouldAddLater, bot, types)
    elif message.text == "📈 Изменить уже готовый":
        showAllTaskLists(message, bot, types)

# Добавление новой задачи
def howManyTaskShouldAddLater(message, bot, types):
    try:
        task_count = int(message.text)
        if 1 <= task_count <= 20:
            user_data[message.chat.id] = {"task_count": task_count, "tasks": []}
            addTaskLater(message, bot, types)
        else:
            bot.send_message(message.chat.id, "Ошибка: введите число от 1 до 20.")
            bot.register_next_step_handler(message, howManyTaskShouldAddLater, bot, types)
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка: введите корректное число.")
        bot.register_next_step_handler(message, howManyTaskShouldAddLater, bot, types)

def addTaskLater(message, bot, types):
    bot.send_message(message.chat.id, "Введите название задачи:")
    bot.register_next_step_handler(message, getTaskName, bot, types)

def getTaskName(message, bot, types):
    task_name = message.text
    user_data[message.chat.id]["tasks"].append({"name": task_name})
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("1👼")
    button2 = types.KeyboardButton("2🙂")
    button3 = types.KeyboardButton("3😢")
    markup.add(button1, button2, button3)
    
    bot.send_message(message.chat.id, "Выберите сложность задачи:", reply_markup=markup)
    bot.register_next_step_handler(message, getTaskDifficulty, bot, types)

def getTaskDifficulty(message, bot, types):
    difficulty_map = {"1👼": 1, "2🙂": 2, "3😢": 3}
    difficulty = difficulty_map.get(message.text)
    
    if difficulty is not None:
        user_data[message.chat.id]["tasks"][-1]["difficulty"] = difficulty
        bot.send_message(message.chat.id, "Введите дату и время напоминания в формате ГГГГ-ММ-ДД ЧЧ:ММ (например, 2024-11-10 14:00):", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, getReminderDate, bot, types)
    else:
        bot.send_message(message.chat.id, "Ошибка: выберите корректную сложность.")
        bot.register_next_step_handler(message, getTaskDifficulty, bot, types)

def getReminderDate(message, bot, types):
    try:
        reminder_date = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        task = user_data[message.chat.id]["tasks"][-1]
        task["reminder_date"] = reminder_date.strftime("%Y-%m-%d %H:%M")
        
        cursor.execute('''
            INSERT INTO tasks (user_id, task_name, difficulty, reminder_date)
            VALUES (?, ?, ?, ?)
        ''', (message.chat.id, task["name"], task["difficulty"], task["reminder_date"]))
        conn.commit()
        
        bot.send_message(message.chat.id, f"Задача '{task['name']}' успешно добавлена и сохранена в базе данных.")
        
        if len(user_data[message.chat.id]["tasks"]) < user_data[message.chat.id]["task_count"]:
            addTaskLater(message, bot, types)
        else:
            bot.send_message(message.chat.id, "Все задачи успешно заданы.")
            user_data.pop(message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка: введите дату в правильном формате.")
        bot.register_next_step_handler(message, getReminderDate, bot, types)

# Просмотр и редактирование всех задач
def showAllTaskLists(message, bot, types):
    """Отображаем все списки задач пользователя."""
    cursor.execute("SELECT DISTINCT task_name FROM tasks WHERE user_id = ?", (message.chat.id,))
    user_tasks = cursor.fetchall()
    
    if not user_tasks:
        bot.send_message(message.chat.id, "У вас нет заданных задач.")
        return

    bot.send_message(message.chat.id, "Ваши списки задач:")
    
    for idx, task in enumerate(user_tasks, start=1):
        bot.send_message(message.chat.id, f"Список {idx} - {task[0]}")
        showTasksInList(message, bot, types, task[0])

def showTasksInList(message, bot, types, list_name):
    """Отображение задач внутри конкретного списка."""
    cursor.execute("SELECT task_id, task_name, difficulty, reminder_date FROM tasks WHERE user_id = ? AND task_name = ?", (message.chat.id, list_name))
    tasks = cursor.fetchall()
    
    response = f"Список задач '{list_name}':\n\n"
    for task in tasks:
        response += (f"ID: {task[0]}\nНазвание: {task[1]}\n"
                     f"Сложность: {task[2]}\nДата: {task[3]}\n"
                     "Команды:\n"
                     f"/edit_{task[0]} - Изменить\n"
                     f"/delete_{task[0]} - Удалить\n\n")
    bot.send_message(message.chat.id, response)

def editTask(message, bot, types):
    """Начало редактирования задачи по её ID."""
    try:
        task_id = int(message.text.split("_")[1])
        user_data[message.chat.id] = {"edit_task_id": task_id}
        bot.send_message(message.chat.id, "Введите новое название задачи:")
        bot.register_next_step_handler(message, updateTaskName, bot, types)
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Ошибка: укажите корректный ID задачи.")

def updateTaskName(message, bot, types):
    task_id = user_data[message.chat.id]["edit_task_id"]
    new_name = message.text
    cursor.execute("UPDATE tasks SET task_name = ? WHERE task_id = ?", (new_name, task_id))
    conn.commit()
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("1👼")
    button2 = types.KeyboardButton("2🙂")
    button3 = types.KeyboardButton("3😢")
    markup.add(button1, button2, button3)
    
    bot.send_message(message.chat.id, "Выберите новую сложность задачи:", reply_markup=markup)
    bot.register_next_step_handler(message, updateTaskDifficulty, bot, types)

def updateTaskDifficulty(message, bot, types):
    task_id = user_data[message.chat.id]["edit_task_id"]
    difficulty_map = {"1👼": 1, "2🙂": 2, "3😢": 3}
    difficulty = difficulty_map.get(message.text)
    
    if difficulty is not None:
        cursor.execute("UPDATE tasks SET difficulty = ? WHERE task_id = ?", (difficulty, task_id))
        conn.commit()
        bot.send_message(message.chat.id, "Введите новую дату и время в формате ГГГГ-ММ-ДД ЧЧ:ММ (например, 2024-11-10 14:00):", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, updateTaskDate, bot, types)
    else:
        bot.send_message(message.chat.id, "Ошибка: выберите корректную сложность.")
        bot.register_next_step_handler(message, updateTaskDifficulty, bot, types)

def updateTaskDate(message, bot, types):
    try:
        task_id = user_data[message.chat.id]["edit_task_id"]
        reminder_date = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        
        cursor.execute("UPDATE tasks SET reminder_date = ? WHERE task_id = ?", (reminder_date.strftime("%Y-%m-%d %H:%M"), task_id))
        conn.commit()
        bot.send_message(message.chat.id, "Задача успешно обновлена.")
        user_data.pop(message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка: введите дату в правильном формате.")
        bot.register_next_step_handler(message, updateTaskDate, bot, types)

def deleteTask(message, bot):
    """Удаление задачи по её ID."""
    try:
        task_id = int(message.text.split("_")[1])
        cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        conn.commit()
        bot.send_message(message.chat.id, "Задача успешно удалена.")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "Ошибка: укажите корректный ID задачи.")
