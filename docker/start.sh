#!/usr/bin/env bash
set -e

echo "Waiting for MySQL..."
until nc -z ${MYSQL_HOST:-mysql} ${MYSQL_PORT:-3306}; do
  sleep 1
done
echo "MySQL is up."

# Временно отключаем миграции
# alembic upgrade head

# Запуск API
exec uvicorn app.main:app --host ${APP_HOST:-0.0.0.0} --port ${APP_PORT:-8000}
