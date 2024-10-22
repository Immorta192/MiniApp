# Используем официальный базовый образ Python
FROM python:3.9-slim

ENV TELEGRAM_TOKEN="7360518240:AAEJ75gYh5IcuiS2tVWvSJfMIF35E7bf4jg"

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip3 install --no-cache-dir -r requirements.txt

# Устанавливаем uvicorn и aiohttp
RUN pip3 install uvicorn

RUN pip3 install aiohttp

# Копируем остальной код приложения в контейнер
COPY . .

# Открываем порт для доступа к приложению
EXPOSE 80

# Команда для запуска приложения
CMD ["python", "Main.py", "--host", "34.126.79.187", "--port", "80"]