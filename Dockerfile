FROM python:3.12-slim

LABEL maintainer="ilnursoft@gmail.com" \
      version="0.2.0" \
      description="Telegram Bot Core with Plugin System"

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash tlgbot

WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml uv.lock ./

# Установка uv и зависимостей
RUN pip install uv && \
    uv sync --frozen

# Копирование исходного кода
COPY --chown=tlgbot:tlgbot . .

# Создание директорий для логов и данных
RUN mkdir -p /app/logs /app/data && \
    chown -R tlgbot:tlgbot /app

# Переключение на непривилегированного пользователя
USER tlgbot

# Переменные окружения
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    TYPE_DB=SQLITE \
    SETTINGS_DB_PATH=/app/data/settings.db

# Health check для проверки работоспособности бота
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sqlite3; conn = sqlite3.connect('${SETTINGS_DB_PATH}'); conn.close()" || exit 1

# Expose порт для потенциальных webhook'ов
EXPOSE 8080

# Точка входа
ENTRYPOINT ["uv", "run", "tlgbotcore"]