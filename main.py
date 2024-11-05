import telebot
bot = telebot.TeleBot('')

@bot.message_handler(commands=['start'])
def startChat(message):
    bot.send_message(message.chat.id, 'Привет')
    
    
bot.polling(none_stop=True)