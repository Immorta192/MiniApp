import logging
import aiohttp
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes


# Функция для получения информации о фильмах через OMDb API
async def search_movies(title: str) -> dict:
    api_key = 'bf196073'
    base_url = 'http://www.omdbapi.com/'
    params = {
        'apikey': api_key,
        's': title  # Используем 's', чтобы искать все фильмы с этим названием
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"Error": "Failed to retrieve data"}


# Функция для получения конкретной информации о фильме
async def get_movie_info(imdb_id: str) -> dict:
    api_key = 'bf196073'
    base_url = 'http://www.omdbapi.com/'
    params = {
        'apikey': api_key,
        'i': imdb_id  # Используем 'i' для поиска по IMDb ID
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


# Функция для обработки текста и поиска фильмов
async def get_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    movie_title = update.message.text
    movies_info = await search_movies(movie_title)

    if "Error" not in movies_info and movies_info.get("Search"):
        keyboard = []
        for movie in movies_info['Search']:
            keyboard.append(
                [InlineKeyboardButton(f"{movie['Title']} ({movie['Year']})", callback_data=movie['imdbID'])])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Выберите нужную часть фильма:', reply_markup=reply_markup)
    else:
        await update.message.reply_text("Не удалось найти информацию о фильме.")


# Функция для обработки выбора фильма пользователем
async def movie_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    movie_id = query.data
    movie_info = await get_movie_info(movie_id)

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

    await query.edit_message_text(reply_message)


if __name__ == '__main__':
    application = ApplicationBuilder().token('7360518240:AAEJ75gYh5IcuiS2tVWvSJfMIF35E7bf4jg').build()

    # Команда /start
    application.add_handler(CommandHandler("start", start))

    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_movie))

    # Обработчик выбора фильма из кнопок
    application.add_handler(CallbackQueryHandler(movie_details))

    application.run_polling()
