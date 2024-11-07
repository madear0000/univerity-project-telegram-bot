import telebot
from telebot import types
from logic import startWork, checkTimeToTask, addStartButton, showStatistics
from saveData import init_db
from doLater import getScheduledTasks
from datetime import datetime
import threading
import time

bot = telebot.TeleBot('7981308623:AAFQFaX8c-yOJZX-hYtG6LPlifqZQfXcTW0')

@bot.message_handler(commands=['start'])
def startChat(message):
    markup = addStartButton(types);
    bot.send_message(message.chat.id, f"""Здравствуйте, {message.from_user.first_name}. Это бот для улучшения вашего тайм-менеджмента и повышения вашей мотивации!
Бот позволяет вам начать цепочку активностей в данный момент или выстроить рабочий график для последующей реализации, а также посмотреть статистику уже выполненных задач.
Хотите задать задачу или посмотреть статистику?""", reply_markup=markup)
    
@bot.message_handler(content_types=['text'])
def chatWithUser(message):
    if (message.text == "📝 Задать задачу"):
         startWork(message, bot, types)
    elif message.text == "👁 Посмотреть статистику":
        showStatistics(message, bot)
    elif message.text in ["🚀 Начать активность сейчас", "🕒 Задать график задач потом", "❌ Отменить действие"]:
        checkTimeToTask(message, bot, types)
        
def checkTaskSchedule():
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        tasks = getScheduledTasks(now)
        
        for task in tasks:
            bot.send_message(
                task[0],  
                f"Напоминание: у вас запланирована задача '{task[1]}' на {task[2]}"
            )
        
        time.sleep(60)  

threading.Thread(target=checkTaskSchedule, daemon=True).start()
        
    
bot.polling(none_stop=True)
init_db()