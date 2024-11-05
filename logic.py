from startNow import howManyTaskShouldAddNow

def addStartButton(types):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    startWorkButton = types.KeyboardButton("📝 Задать задачу")
    markup.add(startWorkButton)
    return markup

def checkTimeToTask(message, bot, types):
    if message.text == "🚀 Начать активность сейчас":
        bot.send_message(message.chat.id, "Хорошо, сколько задач вы хотите задать?", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, howManyTaskShouldAddNow, bot, types)
    elif message.text == "🕒 Задать график задач потом":
        bot.send_message(message.chat.id, "Вы выбрали задать задачу позже.", reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "Отменить действие":
        markup = addStartButton(types)
        bot.send_message(message.chat.id, "Хорошо, задача отменена", reply_markup=markup)

def startWork(message, bot, types):
    markupButtonForTask = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    buttonForTaskNow = types.KeyboardButton("🚀 Начать активность сейчас")
    buttonForTaskLater = types.KeyboardButton("🕒 Задать график задач потом")
    buttonForCancel = types.KeyboardButton("❌ Отменить действие")
    
    markupButtonForTask.add(buttonForTaskNow)
    markupButtonForTask.add(buttonForTaskLater)
    markupButtonForTask.add(buttonForCancel)
    
    bot.send_message(message.chat.id, 'Как вы хотите задать задачу?', reply_markup=markupButtonForTask)
