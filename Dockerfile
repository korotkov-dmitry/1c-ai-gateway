# --- Этап 1: Сборка зависимостей ---
FROM python:3.11-slim AS builder

WORKDIR /build

# Устанавливаем системные инструменты для сборки (если пригодятся для wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы конфигурации зависимостей
COPY pyproject.toml README.md ./

# Скачиваем зависимости в локальную папку колес (wheels), чтобы не тащить лишний кэш pip
RUN pip install --no-cache-dir --user .

# --- Этап 2: Финальный минимальный образ ---
FROM python:3.11-slim AS runner

WORKDIR /app

# Создаем безопасного системного пользователя
RUN useradd -u 8888 appuser && chown -R appuser:appuser /app
USER appuser

# Копируем установленные библиотеки из предыдущего этапа
COPY --from=builder /root/.local /home/appuser/.local

# Копируем всю папку app целиком в /app/app/ внутри контейнера
COPY --chown=appuser:appuser app/ ./app/

# Добавляем путь к установленным пакетам в переменную окружения PATH
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# 🔥 ГЛАВНОЕ ИСПРАВЛЕНИЕ: Говорим Python считать текущую директорию (/app) корнем для импортов.
# Теперь "from app.api.routes ..." отработает идеально!
ENV PYTHONPATH=/app

# Открываем порт
EXPOSE 8000

# 🔥 Запускаем uvicorn, указывая полный путь к модулю через точку относительно корня /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]