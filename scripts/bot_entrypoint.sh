#!/bin/bash

# DB va Web tayyor bo'lishini kutish
echo "Waiting for web and db..."

while ! nc -z db 5432; do
  sleep 1
done

echo "Services started. Compiling locales..."

# Locale fayllarni compile qilish
cd bot/locales
for lang in uz ru en; do
    msgfmt -o $lang/LC_MESSAGES/bot.mo $lang/LC_MESSAGES/bot.po 2>/dev/null || echo "⚠️ $lang compile xatosi"
done
cd ../..

echo "Starting Telegram Bot..."
cd bot
exec python bot.py
