import logging
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from deep_translator import GoogleTranslator

# Словарь для хранения выбора языка
user_language = {}
# Настройка логгера
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция для перевода текста
def translate_text(text: str, lang: str) -> str:
    if lang == 'ru':
        return GoogleTranslator(source='ru', target='en').translate(text)
    elif lang == 'en':
        return GoogleTranslator(source='en', target='ru').translate(text)
    return text

# Функция для выбора языка при старте
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("English", callback_data='lang_en')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Выберите язык / Choose your language:', reply_markup=reply_markup)

# Функция для обработки выбора языка
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Устанавливаем язык для пользователя
    if query.data == 'lang_ru':
        user_language[query.from_user.id] = 'ru'
        await query.edit_message_text("Язык выбран. Введите название фильма.")
    elif query.data == 'lang_en':
        user_language[query.from_user.id] = 'en'
        await query.edit_message_text("Language set. Please enter the movie title.")

# Функция для поиска фильмов
async def search_movies(title: str) -> dict:
    api_key = 'bf196073'  # Ваш API ключ
    base_url = 'http://www.omdbapi.com/'
    params = {
        'apikey': api_key,
        's': title  # Используем 's' для поиска
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"Error": "Failed to retrieve data"}

# Функция для получения информации о конкретном фильме
async def get_movie_info(movie_id: str) -> dict:
    api_key = 'bf196073'  # Ваш API ключ
    base_url = 'http://www.omdbapi.com/'
    params = {
        'apikey': api_key,
        'i': movie_id  # Используем 'i' для получения информации о фильме по ID
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"Error": "Failed to retrieve data"}

# Функция для получения информации о фильме
async def get_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        movie_title = update.message.text
        lang = user_language.get(update.message.from_user.id, 'en')  # По умолчанию английский

        # Переводим текст запроса только если выбран русский язык
        if lang == 'ru':
            translated_title = translate_text(movie_title, lang)
        else:
            translated_title = movie_title

        movies_info = await search_movies(translated_title)

        if "Error" not in movies_info and movies_info.get("Search"):
            keyboard = []
            for movie in movies_info['Search']:
                # Переводим названия фильмов для кнопок в зависимости от выбранного языка
                if lang == 'ru':
                    translated_movie_title = translate_text(f"{movie['Title']} ({movie['Year']})", lang)
                else:
                    translated_movie_title = f"{movie['Title']} ({movie['Year']})"

                keyboard.append([InlineKeyboardButton(translated_movie_title[:30] + "\n" + translated_movie_title[30:],
                                                      callback_data=movie['imdbID'])])

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
    except Exception as e:
        logger.error(f"Ошибка при получении информации о фильме: {e}")


# Функция для получения данных о конкретном фильме
async def movie_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    movie_id = query.data
    movie_info = await get_movie_info(movie_id)
    lang = user_language.get(query.from_user.id, 'en')

    if "Error" not in movie_info:
        # Переводим описание фильма и его детали в зависимости от выбранного языка
        if lang == 'ru':
            reply_message = (
                f"Название: {translate_text(movie_info.get('Title'), lang)}\n"
                f"Год: {movie_info.get('Year')}\n"
                f"Режиссёр: {translate_text(movie_info.get('Director'), lang)}\n"
                f"Жанр: {translate_text(movie_info.get('Genre'), lang)}\n"
                f"Рейтинг: {movie_info.get('imdbRating')}\n"
                f"Описание: {translate_text(movie_info.get('Plot'), lang)}\n"
            )
        else:
            reply_message = (
                f"Title: {translate_text(movie_info.get('Title'), lang)}\n"
                f"Year: {movie_info.get('Year')}\n"
                f"Director: {translate_text(movie_info.get('Director'), lang)}\n"
                f"Genre: {translate_text(movie_info.get('Genre'), lang)}\n"
                f"IMDb Rating: {movie_info.get('imdbRating')}\n"
                f"Plot: {translate_text(movie_info.get('Plot'), lang)}\n"
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
