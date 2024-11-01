import logging
import aiohttp
import os
from telegram import (Update, KeyboardButton, WebAppInfo, ReplyKeyboardMarkup)
from telegram.ext import (ApplicationBuilder, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler)

# Настройка логгера
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для отображения кнопки "Start"
async def show_start_button(update: Update, context: CallbackContext) -> None:
    kb = [[KeyboardButton("Start")]]
    reply_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Нажмите кнопку 'Start' для начала работы с ботом:", reply_markup=reply_markup)

# Функция для обработки нажатия на кнопку "Start"
async def start_button_action(update: Update, context: CallbackContext) -> None:
    kb = [[KeyboardButton("Open MiniApp", web_app=WebAppInfo(url="https://immorta192.github.io/MiniApp/"))]]
    await update.message.reply_text("Бот запущен! Нажмите кнопку ниже, чтобы открыть мини-приложение:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))


# Функция для поиска фильмов
async def search_movies(title: str) -> dict:
    api_key = 'bf196073'  # Ваш API ключ
    base_url = 'http://www.omdbapi.com/'
    params = {'apikey': api_key, 's': title}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Ошибка при получении данных с OMDb API: статус {response.status}")
                    return {"Error": "Failed to retrieve data"}
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса: {e}")
        return {"Error": str(e)}

# Функция для получения информации о конкретном фильме
async def get_movie_info(movie_id: str) -> dict:
    api_key = 'bf196073'  # Ваш API ключ
    base_url = 'http://www.omdbapi.com/'
    params = {'apikey': api_key, 'i': movie_id}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Ошибка при получении данных о фильме с OMDb API: статус {response.status}")
                    return {"Error": "Failed to retrieve data"}
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса: {e}")
        return {"Error": str(e)}

# Функция для обработки текстовых сообщений
async def get_movie(update: Update, context: CallbackContext) -> None:
    try:
        movie_title = update.message.text
        movies_info = await search_movies(movie_title)

        if "Error" not in movies_info and movies_info.get("Search"):
            keyboard = [[KeyboardButton(f"{movie['Title']} ({movie['Year']})", callback_data=movie['imdbID'])] for movie in movies_info['Search']]
            reply_markup = ReplyKeyboardMarkup(keyboard)
            await update.message.reply_text('Выберите нужный фильм:', reply_markup=reply_markup)
        else:
            await update.message.reply_text("Не удалось найти информацию о фильме.")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте снова.")

# Функция для обработки нажатия на кнопку фильма
async def movie_details(update: Update, context: CallbackContext) -> None:
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

        poster_url = movie_info.get('Poster')
        if poster_url and poster_url != 'N/A':
            await query.edit_message_text(reply_message, disable_web_page_preview=True)
            await query.message.reply_photo(photo=poster_url)
        else:
            await query.edit_message_text(reply_message)
    else:
        await query.edit_message_text("Ошибка при получении информации о фильме.")


if __name__ == '__main__':
    # Получение токена из переменной окружения
    token = os.environ.get('TELEGRAM_TOKEN')

    # Проверка, был ли токен успешно получен
    if not token:
        raise ValueError("No token provided. Set the TELEGRAM_TOKEN environment variable.")

    application = ApplicationBuilder().token(token).build()

    # Обработчик для нажатия на кнопку "Start"
    application.add_handler(MessageHandler(filters.Regex("^Start$"), start_button_action))

    # Обработчик для текстовых сообщений (вызывает кнопку "Start" при первом запуске)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, show_start_button))

    # Обработчик для поиска фильмов
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_movie))

    # Обработчик для получения деталей фильма
    application.add_handler(CallbackQueryHandler(movie_details))

    # Запуск бота
    application.run_polling()
