import telebot
from telebot import types;
from logic import startWork
from logic import checkTimeToTask
from logic import addStartButton

bot = telebot.TeleBot('7981308623:AAFQFaX8c-yOJZX-hYtG6LPlifqZQfXcTW0')

@bot.message_handler(commands=['start'])
def startChat(message):
    markup = addStartButton(types);
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}', reply_markup=markup)
    
@bot.message_handler(content_types=['text'])
def chatWithUser(message):
    if (message.text == "Задать задачу"):
         startWork(message, bot, types)
    elif message.text in ["Сейчас", "Потом", "Отмена"]:
        checkTimeToTask(message, bot, types)
        
    
bot.polling(none_stop=True)