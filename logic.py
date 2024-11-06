from startNow import howManyTaskShouldAddNow
from saveData import get_statistics 

def addStartButton(types):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    startWorkButton = types.KeyboardButton("📝 Задать задачу")
    viewStatsButton = types.KeyboardButton("👁 Посмотреть статистику")
    markup.add(startWorkButton, viewStatsButton)
    return markup

def checkTimeToTask(message, bot, types):
    if message.text == "🚀 Начать активность сейчас":
        bot.send_message(message.chat.id, "Хорошо, сколько задач вы хотите задать?", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, howManyTaskShouldAddNow, bot, types)
    elif message.text == "🕒 Задать график задач потом":
        bot.send_message(message.chat.id, "Вы выбрали задать задачу позже.", reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "❌ Отменить действие":
        markup = addStartButton(types)
        bot.send_message(message.chat.id, "Хорошо, задача отменена", reply_markup=markup)
        
def showStatistics(message, bot):
    total_tasks, total_time, difficulty_stats = get_statistics(message.chat.id)
    
    if total_tasks == 0:
        bot.send_message(message.chat.id, "У вас пока нет выполненных задач.")
    else:
        stats_message = f"📊 Ваша статистика:\n\n" \
                        f"Всего выполнено задач: {total_tasks}\n" \
                        f"Общее время: {total_time} минут\n\n" \
                        f"Сложности задач:\n" \
                        f"Легкие задачи: {difficulty_stats['easy']} 👼\n" \
                        f"Средние задачи: {difficulty_stats['medium']} 🙂\n" \
                        f"Сложные задачи: {difficulty_stats['hard']} 😢"
        
        bot.send_message(message.chat.id, stats_message)

def startWork(message, bot, types):
    markupButtonForTask = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    buttonForTaskNow = types.KeyboardButton("🚀 Начать активность сейчас")
    buttonForTaskLater = types.KeyboardButton("🕒 Задать график задач потом")
    buttonForCancel = types.KeyboardButton("❌ Отменить действие")
    
    markupButtonForTask.add(buttonForTaskNow)
    markupButtonForTask.add(buttonForTaskLater)
    markupButtonForTask.add(buttonForCancel)
    
    bot.send_message(message.chat.id, 'Как вы хотите задать задачу?', reply_markup=markupButtonForTask)