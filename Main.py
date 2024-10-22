import logging
import aiohttp  # Используем aiohttp для асинхронных запросов
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes


# Функция для получения информации о фильме через OMDb API
async def get_movie_info(title: str) -> dict:
    api_key = 'bf196073'
    base_url = 'http://www.omdbapi.com/'
    params = {
        'apikey': api_key,
        't': title
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"Error": "Failed to retrieve data"}


# Логирование для удобства отладки
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


# Функция для ответа бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Введи название фильма, чтобы узнать о нём информацию.')


# Функция для обработки текста и отправки запроса на OMDb API
async def get_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    movie_title = update.message.text
    movie_info = await get_movie_info(movie_title)  # Добавлено await

    if "Error" not in movie_info:
        reply_message = (
            f"Название: {movie_info.get('Title')}\n"
            f"Год: {movie_info.get('Year')}\n"
            f"Режиссёр: {movie_info.get('Director')}\n"
            f"Жанр: {movie_info.get('Genre')}\n"
            f"Рейтинг: {movie_info.get('imdbRating')}\n"
            f"Описание: {movie_info.get('Plot')}\n"
        )
    else:
        reply_message = "Не удалось найти информацию о фильме."

    await update.message.reply_text(reply_message)


if __name__ == '__main__':
    application = ApplicationBuilder().token('7360518240:AAEJ75gYh5IcuiS2tVWvSJfMIF35E7bf4jg').build()

    # Команда /start
    application.add_handler(CommandHandler("start", start))

    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_movie))

    application.run_polling()
