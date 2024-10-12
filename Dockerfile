# Используем официальный базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip3 install --no-cache-dir -r requirements.txt

# Устанавливаем uvicorn
RUN pip3 install uvicorn

# Копируем остальной код приложения в контейнер
COPY . .

# Открываем порт 80 для доступа к приложению
EXPOSE 80

# Команда для запуска приложения
CMD ["uvicorn", "Main:app", "--host", "0.0.0.0", "--port", "80"]