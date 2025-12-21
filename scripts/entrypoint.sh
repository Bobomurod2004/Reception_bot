#!/bin/bash
set -e

# Port bo'shligini tekshirish uchun nc kutish
echo "Waiting for postgres..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

# Migratsiyalarni amalga oshirish
echo "Applying database migrations..."
python manage.py migrate --noinput

# Statik fayllarni yig'ish (CSS, JS)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Gunicorn ni ishga tushirish
echo "Starting gunicorn..."
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --timeout 120
