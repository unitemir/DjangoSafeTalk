# Используйте официальный образ Python как родительский образ
FROM python:3.9

# Установите рабочую директорию в контейнере
WORKDIR /usr/src/app

# Установите переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Обновление списка пакетов и установка netcat
RUN apt-get update && \
    apt-get install -y netcat-openbsd postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Установите зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируйте содержимое локальной директории в рабочую директорию контейнера
COPY . .

# Добавьте скрипт для выполнения миграции и запуска приложения
COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# Задайте скрипт entrypoint, который будет запускаться при старте контейнера
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

# По умолчанию запускайте Gunicorn
CMD ["gunicorn", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "4", "--bind", "0.0.0.0:8000", "django_safe_talk.asgi:application"]

