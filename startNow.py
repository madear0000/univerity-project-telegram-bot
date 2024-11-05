import time
import sqlite3
from datetime import datetime

user_tasks = {}

def create_db():
    conn = sqlite3.connect('tasks.db') 
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS completed_tasks (
        task_name TEXT,
        difficulty INTEGER,
        time INTEGER,
        completion_time TEXT
    )
    ''')

    conn.commit() 
    conn.close()  
    
def log_completed_task(task_name, difficulty, time):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    completion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
    INSERT INTO completed_tasks (task_name, difficulty, time, completion_time)
    VALUES (?, ?, ?, ?)
    ''', (task_name, difficulty, time, completion_time))

    conn.commit() 
    conn.close()  

def isUserDoHisTask(message, bot, index, types):
    if message.text == "✅ Да":
        bot.send_message(message.chat.id, f"Отлично, задача {index} завершена!")
        startNextTask(message, bot, index, types) 
    else:
        bot.send_message(message.chat.id, "Не расстраивайся, попробуй еще раз.")
        startDoTask(message, bot, types) 

def startNextTask(message, bot, current_index, types):
    user_id = message.chat.id
    tasks = user_tasks[user_id]
    if current_index < len(tasks): 
        index = current_index + 1
        task, details = list(tasks.items())[current_index]  
        difficulty = details["difficulty"]
        time_to_complete = details["time"]

        bot.send_message(message.chat.id, f"Начинаем задачу {index}: {task}. Удачи вам в усердной работе!", reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(message.chat.id, f"Время выполнения задачи: {time_to_complete} минут.")
        time.sleep(time_to_complete * 60)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        no_button = types.KeyboardButton("❌ Нет")
        yes_button = types.KeyboardButton("✅ Да")
        markup.add(yes_button, no_button)

        bot.send_message(message.chat.id, f"Время для выполнения задачи истекло. Вы закончили?", reply_markup=markup)
        bot.register_next_step_handler(message, isUserDoHisTask, bot, index, types)  # Передаем types
    else:
        from logic import startWork
        markup = startWork(types)
        bot.send_message(message.chat.id, "Вы завершили все задачи! Молодец!", reply_markup=markup)

def startDoTask(message, bot, types):
    user_id = message.chat.id
    if user_id not in user_tasks or not user_tasks[user_id]:
        bot.send_message(message.chat.id, "Нет добавленных задач.")
        return

    tasks = user_tasks[user_id]
    index = 0
    task, details = list(tasks.items())[index] 
    difficulty = details["difficulty"]
    time_to_complete = details["time"]

    bot.send_message(message.chat.id, f"Начинаем задачу {index + 1}: {task}. Удачи вам в усердной работе!", reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, f"Время выполнения задачи: {time_to_complete} минут.")
    time.sleep(time_to_complete * 60)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    no_button = types.KeyboardButton("❌ Нет")
    yes_button = types.KeyboardButton("✅ Да")
    markup.add(yes_button, no_button)

    bot.send_message(message.chat.id, f"Время для выполнения задачи истекло. Вы закончили?", reply_markup=markup)
    bot.register_next_step_handler(message, isUserDoHisTask, bot, index + 1, types)  

def addTaskNow(message, bot, task_count, types, current_task_number=1):
    user_id = message.chat.id
    if user_id not in user_tasks:
        user_tasks[user_id] = {}

    if current_task_number > task_count:
        bot.send_message(message.chat.id, "Все задачи добавлены!")
        displayTasks(message, bot, types)
        return

    bot.send_message(message.chat.id, f"Введите задачу {current_task_number} из {task_count}:", reply_markup=types.ReplyKeyboardRemove())
    
    bot.register_next_step_handler(message, getTaskDetails, bot, task_count, types, current_task_number)

def getTaskDetails(message, bot, task_count, types, current_task_number):
    user_id = message.chat.id
    task = message.text
    if user_id not in user_tasks:
        user_tasks[user_id] = {}
    user_tasks[user_id][task] = {"difficulty": None, "time": None} 

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("1👼")  
    button2 = types.KeyboardButton("2🙂")    
    button3 = types.KeyboardButton("3😢")    
    markup.add(button1, button2, button3)

    bot.send_message(message.chat.id, "Оцените сложность задачи:", reply_markup=markup)
    bot.register_next_step_handler(message, setTaskDifficulty, bot, task, task_count, types, current_task_number)

def setTaskDifficulty(message, bot, task, task_count, types, current_task_number):
    user_id = message.chat.id
    try:
        difficulty = int(message.text[0])  
        if difficulty in [1, 2, 3]:
            user_tasks[user_id][task]["difficulty"] = difficulty
            
            bot.send_message(message.chat.id, f"Введите время выполнения задачи (в минутах): {current_task_number} из {task_count}:", reply_markup=types.ReplyKeyboardRemove())
            
            bot.register_next_step_handler(message, setTaskTime, bot, task, task_count, types, current_task_number)
        else:
            bot.send_message(message.chat.id, "Ошибка: введите корректную оценку сложности (1, 2 или 3).")
            setTaskDifficulty(message, bot, task, task_count, types, current_task_number)
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка: введите корректное число.")
        setTaskDifficulty(message, bot, task, task_count, types, current_task_number)

def setTaskTime(message, bot, task, task_count, types, current_task_number):
    user_id = message.chat.id
    try:
        time = int(message.text)
        if time >= 0:
            user_tasks[user_id][task]["time"] = time
            
            current_task_number += 1
            addTaskNow(message, bot, task_count, types, current_task_number) 
        else:
            bot.send_message(message.chat.id, "Ошибка: время должно быть неотрицательным.")
            setTaskTime(message, bot, task, task_count, types, current_task_number)
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка: введите корректное число.")
        setTaskTime(message, bot, task, task_count, types, current_task_number)

def displayTasks(message, bot, types):
    user_id = message.chat.id
    if user_id not in user_tasks or not user_tasks[user_id]:
        bot.send_message(message.chat.id, "Нет добавленных задач.")
        return
    
    for index, (task, details) in enumerate(user_tasks[user_id].items(), start=1):
        bot.send_message(message.chat.id, f"Задача {index}: {task}, Сложность: {details['difficulty']}, Время: {details['time']} минут")
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    edit_button = types.KeyboardButton("✏️ Изменить данные")
    delete_button = types.KeyboardButton("❌ Удалить задачу")
    ok_button = types.KeyboardButton("✅ Все верно")
    markup.add(ok_button)
    markup.add(edit_button)
    markup.add(delete_button)
    bot.send_message(message.chat.id, "Хотите изменить данные или удалить задачу?", reply_markup=markup)
    
    bot.register_next_step_handler(message, handleEditOrDelete, bot, types)

def handleEditOrDelete(message, bot, types):
    user_id = message.chat.id
    if user_id not in user_tasks or not user_tasks[user_id]:
        bot.send_message(message.chat.id, "Нет добавленных задач.")
        return

    if message.text == "✏️ Изменить данные":
        bot.send_message(message.chat.id, "Введите номер задачи, которую хотите изменить:")
        bot.register_next_step_handler(message, editTask, bot, types)
    elif message.text == "❌ Удалить задачу":
        bot.send_message(message.chat.id, "Введите номер задачи, которую хотите удалить:")
        bot.register_next_step_handler(message, deleteTask, bot, types)
    elif message.text == "✅ Все верно":
        bot.send_message(message.chat.id, "Хорошо, тогда давайте приступать к выполнению")
        startDoTask(message, bot, types)
    else:
        bot.send_message(message.chat.id, "Ошибка: выберите действие.")
        displayTasks(message, bot, types)

def editTask(message, bot, types):
    user_id = message.chat.id
    try:
        task_number = int(message.text) - 1
        task_keys = list(user_tasks[user_id].keys())
        if 0 <= task_number < len(task_keys):
            task = task_keys[task_number]
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            edit_name = types.KeyboardButton("✏️ Исправить название")
            edit_time = types.KeyboardButton("⏰ Исправить время")
            edit_difficulty = types.KeyboardButton("🔢 Исправить сложность")
            markup.add(edit_name, edit_time, edit_difficulty)
            bot.send_message(message.chat.id, "Выберите, что хотите изменить:", reply_markup=markup)
            bot.register_next_step_handler(message, lambda msg: confirmEdit(msg, bot, task, types))
        else:
            bot.send_message(message.chat.id, "Ошибка: выберите корректный номер задачи.")
            displayTasks(message, bot, types)
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка: введите корректный номер.")
        displayTasks(message, bot, types)

def confirmEdit(message, bot, task, types):
    if message.text == "✏️ Исправить название":
        bot.send_message(message.chat.id, "Введите новое название задачи:")
        bot.register_next_step_handler(message, updateTaskName, bot, task, types)
    elif message.text == "⏰ Исправить время":
        bot.send_message(message.chat.id, "Введите новое время выполнения задачи (в минутах):")
        bot.register_next_step_handler(message, updateTaskTime, bot, task, types)
    elif message.text == "🔢 Исправить сложность":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("1👼")  
        button2 = types.KeyboardButton("2🙂")    
        button3 = types.KeyboardButton("3😢")    
        markup.add(button1, button2, button3)
        bot.send_message(message.chat.id, "Оцените новую сложность задачи:", reply_markup=markup)
        bot.register_next_step_handler(message, lambda msg: updateTaskDifficulty(msg, bot, task, types))
    else:
        bot.send_message(message.chat.id, "Ошибка: выберите действие.")
        displayTasks(message, bot, types)

def updateTaskTime(message, bot, task, types):
    user_id = message.chat.id
    try:
        time = int(message.text)
        if time >= 0:
            user_tasks[user_id][task]["time"] = time  # Обновляем время задачи
            bot.send_message(message.chat.id, f"Время задачи изменено на {time} минут.")
            displayTasks(message, bot, types)
        else:
            bot.send_message(message.chat.id, "Ошибка: время должно быть неотрицательным.")
            updateTaskTime(message, bot, task, types)
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка: введите корректное число.")
        updateTaskTime(message, bot, task, types)

def updateTaskName(message, bot, task, types):
    user_id = message.chat.id
    new_name = message.text
    user_tasks[user_id][new_name] = user_tasks[user_id].pop(task)  
    bot.send_message(message.chat.id, f"Задача переименована в {new_name}.")
    displayTasks(message, bot, types)
    
def updateTaskDifficulty(message, bot, task, types):
    user_id = message.chat.id
    try:
        difficulty = int(message.text[0])  # Сложность задачи
        if difficulty in [1, 2, 3]:
            user_tasks[user_id][task]["difficulty"] = difficulty  # Обновляем сложность задачи
            bot.send_message(message.chat.id, f"Сложность задачи изменена на {difficulty}.")
            displayTasks(message, bot, types)
        else:
            bot.send_message(message.chat.id, "Ошибка: введите корректную оценку сложности (1, 2 или 3).")
            updateTaskDifficulty(message, bot, task, types)
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка: введите корректное число.")
        updateTaskDifficulty(message, bot, task, types)

def deleteTask(message, bot, types):
    user_id = message.chat.id
    try:
        task_number = int(message.text) - 1
        task_keys = list(user_tasks[user_id].keys())
        if 0 <= task_number < len(task_keys):
            task = task_keys[task_number]
            del user_tasks[user_id][task]  # Удаляем задачу
            bot.send_message(message.chat.id, f"Задача '{task}' удалена.")
            displayTasks(message, bot, types)
        else:
            bot.send_message(message.chat.id, "Ошибка: выберите корректный номер задачи.")
            displayTasks(message, bot, types)
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка: введите корректный номер.")
        displayTasks(message, bot, types)


def howManyTaskShouldAddNow(message, bot, types):
    try:
        task_count = int(message.text)
        if 1 <= task_count <= 20:
            addTaskNow(message, bot, task_count, types)
        else:
            bot.send_message(message.chat.id, "Ошибка: введите число от 1 до 20.")
            bot.register_next_step_handler(message, howManyTaskShouldAddNow, bot, types)
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка: введите корректное число.")
        bot.register_next_step_handler(message, howManyTaskShouldAddNow, bot, types)