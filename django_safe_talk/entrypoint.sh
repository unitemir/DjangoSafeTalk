#!/bin/bash

# Проверка доступности базы данных перед выполнением миграций
# Это полезно, когда используется база данных в отдельном сервисе (например, Postgres в Docker Compose)
# и нужно дождаться её полного запуска
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database started"

# Применение миграций
python manage.py migrate

# Сбор статических файлов, если это необходимо
python manage.py collectstatic --noinput --clear

# Запуск Gunicorn
exec gunicorn django_safe_talk.asgi:application --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
