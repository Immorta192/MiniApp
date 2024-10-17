from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

# Создаём основное приложение
app = ApplicationBuilder().token("7360518240:AAEJ75gYh5IcuiS2tVWvSJfMIF35E7bf4jg").build()

# Функция для старта бота
async def start(update: Update, context):
    keyboard = [
        [
            InlineKeyboardButton("Писюлька 1", callback_data='1'),
            InlineKeyboardButton("Ну вторая кнопка и что 2", callback_data='2'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выбери опцию:', reply_markup=reply_markup)

# Функция для обработки нажатий кнопок
async def button(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Ответ нажатия
    if query.data == '1':
        await query.edit_message_text(text="Ты нажал Кнопку 1")
    elif query.data == '2':
        await query.edit_message_text(text="Ты нажал Кнопку 2")

# Добавляем обработчики
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

# Запуск приложения
if __name__ == '__main__':
    app.run_polling()
