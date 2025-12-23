#!/bin/bash
set -e

echo "🌐 Starting Django Web Server..."

# PostgreSQL kutish
echo "⏳ Waiting for PostgreSQL..."
max_attempts=60
attempt=0
while [ $attempt -lt $max_attempts ]; do
  if nc -z ${DB_HOST:-db} ${DB_PORT:-5432} 2>/dev/null; then
    echo "✅ PostgreSQL ready"
    break
  fi
  attempt=$((attempt + 1))
  sleep 1
done

if [ $attempt -eq $max_attempts ]; then
  echo "❌ PostgreSQL not ready after $max_attempts attempts"
  exit 1
fi

# Logs directory yaratish
mkdir -p /app/logs

# Migratsiyalarni amalga oshirish
echo "📊 Applying database migrations..."
python manage.py migrate --noinput

# Statik fayllarni yig'ish (CSS, JS)
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Health check endpoint yaratish (agar yo'q bo'lsa)
if ! grep -q "health" /app/core/urls.py 2>/dev/null; then
    echo "💚 Health check endpoint will be available at /health/"
fi

# Gunicorn ni ishga tushirish
echo "🚀 Starting Gunicorn..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-4} \
    --worker-class sync \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL:-info} \
    --capture-output
