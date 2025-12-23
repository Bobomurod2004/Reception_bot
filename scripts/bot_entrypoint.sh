#!/bin/bash
set -e

echo "🤖 Starting Telegram Bot..."

# DB va Web tayyor bo'lishini kutish
echo "⏳ Waiting for database..."
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
  sleep 1
done
echo "✅ Database ready"

echo "⏳ Waiting for Django API..."
max_attempts=60
attempt=0
while [ $attempt -lt $max_attempts ]; do
  if curl -f -s http://web:8000/health/ > /dev/null 2>&1; then
    echo "✅ Django API ready"
    break
  fi
  attempt=$((attempt + 1))
  sleep 2
done

if [ $attempt -eq $max_attempts ]; then
  echo "❌ Django API not ready after $max_attempts attempts"
  exit 1
fi

# Locale fayllarni compile qilish
echo "🌐 Compiling locales..."
cd /app/bot/locales
for lang in uz ru en; do
    if [ -f "$lang/LC_MESSAGES/bot.po" ]; then
        msgfmt -o $lang/LC_MESSAGES/bot.mo $lang/LC_MESSAGES/bot.po 2>/dev/null || echo "⚠️ $lang compile xatosi"
    fi
done
cd /app

# Bot dependencies o'rnatish (agar kerak bo'lsa)
if [ -f "/app/bot_requirements.txt" ]; then
    echo "📦 Installing bot dependencies..."
    pip install --no-cache-dir -q -r /app/bot_requirements.txt
fi

# Logs directory yaratish
mkdir -p /app/logs

echo "🚀 Starting Telegram Bot..."
cd /app/bot
exec python bot.py
