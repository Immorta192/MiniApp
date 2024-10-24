import logging
import aiohttp
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from googletrans import Translator  # Подключаем библиотеку googletrans для перевода

# Логирование для удобства отладки
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Глобальная переменная для хранения языка пользователя
user_language = {}


# Функция для выбора языка
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите язык / Choose a language:', reply_markup=reply_markup)


# Функция для установки языка
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'lang_ru':
        user_language[query.from_user.id] = 'ru'
        await query.edit_message_text('Язык установлен: Русский. Введите название фильма.')
    elif query.data == 'lang_en':
        user_language[query.from_user.id] = 'en'
        await query.edit_message_text('Language set: English. Enter the movie title.')


# Функция для перевода русского текста на английский
def translate_text(text: str, lang: str) -> str:
    if lang == 'ru':
        translator = Translator()
        translated = translator.translate(text, src='ru', dest='en')
        return translated.text
    return text  # Если язык английский, перевод не требуется


# Функция для получения информации о фильмах через OMDb API
async def search_movies(title: str) -> dict:
    api_key = 'bf196073'
    base_url = 'http://www.omdbapi.com/'
    params = {
        'apikey': api_key,
        's': title
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
        'i': imdb_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"Error": "Failed to retrieve data"}


# Функция для обработки текста и поиска фильмов
async def get_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    movie_title = update.message.text
    lang = user_language.get(update.message.from_user.id, 'en')  # По умолчанию английский

    # Переводим текст, если выбран русский язык
    translated_title = translate_text(movie_title, lang)

    movies_info = await search_movies(translated_title)

    if "Error" not in movies_info and movies_info.get("Search"):
        keyboard = []
        for movie in movies_info['Search']:
            # Добавляем по одной кнопке на строку, чтобы текст помещался
            keyboard.append(
                [InlineKeyboardButton(f"{movie['Title']} ({movie['Year']})", callback_data=movie['imdbID'])])

        reply_markup = InlineKeyboardMarkup(keyboard)
        if lang == 'ru':
            await update.message.reply_text('Выберите нужную часть фильма:', reply_markup=reply_markup)
        else:
            await update.message.reply_text('Select the movie part:', reply_markup=reply_markup)
    else:
        if lang == 'ru':
            await update.message.reply_text("Не удалось найти информацию о фильме.")
        else:
            await update.message.reply_text("Failed to find movie information.")


# Функция для обработки выбора фильма пользователем
async def movie_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    movie_id = query.data
    movie_info = await get_movie_info(movie_id)
    lang = user_language.get(query.from_user.id, 'en')

    if "Error" not in movie_info:
        if lang == 'ru':
            reply_message = (
                f"Название: {movie_info.get('Title')}\n"
                f"Год: {movie_info.get('Year')}\n"
                f"Режиссёр: {movie_info.get('Director')}\n"
                f"Жанр: {movie_info.get('Genre')}\n"
                f"Рейтинг: {movie_info.get('imdbRating')}\n"
                f"Описание: {movie_info.get('Plot')}\n"
            )
        else:
            reply_message = (
                f"Title: {movie_info.get('Title')}\n"
                f"Year: {movie_info.get('Year')}\n"
                f"Director: {movie_info.get('Director')}\n"
                f"Genre: {movie_info.get('Genre')}\n"
                f"IMDb Rating: {movie_info.get('imdbRating')}\n"
                f"Plot: {movie_info.get('Plot')}\n"
            )
    else:
        reply_message = "Error retrieving movie information."

    await query.edit_message_text(reply_message)


if __name__ == '__main__':
    application = ApplicationBuilder().token('7360518240:AAEJ75gYh5IcuiS2tVWvSJfMIF35E7bf4jg').build()

    # Команда /start
    application.add_handler(CommandHandler("start", choose_language))

    # Обработчик выбора языка
    application.add_handler(CallbackQueryHandler(set_language, pattern="^lang_"))

    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_movie))

    # Обработчик выбора фильма из кнопок
    application.add_handler(CallbackQueryHandler(movie_details))

    application.run_polling()
