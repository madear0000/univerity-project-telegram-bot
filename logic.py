

def addStartButton(types):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    startWorkButton = types.KeyboardButton("Задать задачу")
    markup.add(startWorkButton)
    return markup

def checkTimeToTask(message, bot, types):
    if message.text == "Сейчас":
        bot.send_message(message.chat.id, "Хорошо, сколько задач вы хотите задать?")
    elif message.text == "Потом":
        bot.send_message(message.chat.id, "Вы выбрали задать задачу позже.")
    elif message.text == "Отмена":
        markup = addStartButton(types)
        bot.send_message(message.chat.id, "Хорошо задача отменена", reply_markup=markup)

def startWork(message, bot, types):
    markupButtonForTask = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttonForTaskNow = types.KeyboardButton("Сейчас")
    buttonForTaskLater = types.KeyboardButton("Потом")
    buttonForCancel = types.KeyboardButton("Отмена")
    markupButtonForTask.add(buttonForTaskNow, buttonForTaskLater, buttonForCancel)
    bot.send_message(message.chat.id, f'Хорошо когда вы хотите задать задачу', reply_markup=markupButtonForTask)
    