#!/bin/sh

set -e

# Переходим в директорию с Alembic (если нужно)
cd /app

# Применяем миграции
alembic upgrade head
ROOT_PATH="${ROOT_PATH:-}"
# Запускаем FastAPI
exec uvicorn main:app --host 0.0.0.0 --port 8000 --root-path "$ROOT_PATH"