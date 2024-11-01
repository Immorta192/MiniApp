import logging
import aiohttp
import json

from telegram import (Update, KeyboardButton, InlineKeyboardButton,WebAppInfo,
                      InlineKeyboardMarkup, ReplyKeyboardMarkup)


from telegram.ext import (ApplicationBuilder,
                          CommandHandler,CallbackContext,
                          MessageHandler, filters,
                          CallbackQueryHandler, ContextTypes)


# Настройка логгера
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
async def launch_web_ui(update: Update, callback: CallbackContext):
    # For now, we just display google.com...
    kb = [
        [KeyboardButton("Show me Google!", web_app=WebAppInfo("https://google.com"))]
    ]
    await update.message.reply_text("Let's do this...", reply_markup=ReplyKeyboardMarkup(kb))

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

# Функция для получения информации о фильме
async def get_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        movie_title = update.message.text

        # Поиск фильмов
        movies_info = await search_movies(movie_title)

        # Максимальная длина строки в кнопке
        max_length = 40

        if "Error" not in movies_info and movies_info.get("Search"):
            keyboard = []
            for movie in movies_info['Search']:
                full_title = f"{movie['Title']} ({movie['Year']})"

                # Разбиваем название на две строки, если оно слишком длинное
                button_text = full_title if len(full_title) <= max_length else full_title[:max_length//2] + "\n" + full_title[max_length//2:]

                keyboard.append([InlineKeyboardButton(button_text, callback_data=movie['imdbID'])])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                'Выберите нужную часть фильма:',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("Не удалось найти информацию о фильме.")

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте снова.")

# Функция для получения данных о конкретном фильме
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

        # URL обложки
        poster_url = movie_info.get('Poster')
        if poster_url and poster_url != 'N/A':  # Проверяем, что обложка есть
            await query.edit_message_text(reply_message, disable_web_page_preview=True)
            await query.message.reply_photo(photo=poster_url)  # Отправляем обложку
        else:
            await query.edit_message_text(reply_message)
    else:
        reply_message = "Ошибка при получении информации о фильме."
        await query.edit_message_text(reply_message)

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Введите название фильма:")

if __name__ == '__main__':
    application = ApplicationBuilder().token('7360518240:AAEJ75gYh5IcuiS2tVWvSJfMIF35E7bf4jg').build()

    application.add_handler(CommandHandler("start", start))  # Обработчик для /start
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_movie))
    application.add_handler(CallbackQueryHandler(movie_details))

    application.run_polling()
