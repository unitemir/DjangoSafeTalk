#!/bin/bash

# Проверка доступности базы данных перед выполнением миграций
echo "Waiting for database..."
# Увеличим количество попыток и интервал ожидания
max_attempts=30  # Количество попыток подключения
attempt=1        # Счетчик попыток

# Используем цикл для проверки доступности порта и готовности базы
while ! nc -z db 5432; do
  if [ $attempt -ge $max_attempts ]; then
    echo "Database is not available after $max_attempts attempts... exiting."
    exit 1
  fi

  echo "Database not ready yet. Attempt $attempt of $max_attempts..."
  sleep 2  # Увеличиваем интервал ожидания
  attempt=$(( $attempt + 1 ))
done
echo "Database started"

# После успешного подключения к порту, проверим с помощью pg_isready
echo "Checking if PostgreSQL is ready..."
while ! pg_isready -h db -p 5432 -U $POSTGRES_USER; do
  if [ $attempt -ge $max_attempts ]; then
    echo "PostgreSQL is not ready after $max_attempts attempts... exiting."
    exit 1
  fi

  echo "PostgreSQL not ready yet. Attempt $attempt of $max_attempts..."
  sleep 2
  attempt=$(( $attempt + 1 ))
done
echo "PostgreSQL is ready."

# Применение миграций
python manage.py migrate

# Сбор статических файлов, если это необходимо
python manage.py collectstatic --noinput --clear

# Запуск Gunicorn
exec gunicorn django_safe_talk.asgi:application --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
