# Используем Python 3.11
FROM python:3.11

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы проекта внутрь контейнера
COPY . .

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Открываем порт для Django
EXPOSE 8000

# Запуск сервера (без миграций)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
