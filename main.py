import telebot


bot = telebot.TeleBot('7981308623:AAFQFaX8c-yOJZX-hYtG6LPlifqZQfXcTW0')

@bot.message_handler(commands=['start'])
def startChat(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}')
    
bot.polling(none_stop=True)