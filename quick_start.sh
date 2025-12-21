#!/bin/bash

echo "🚀 Tezkor ishga tushirish..."

# .env fayl tekshirish
if [ ! -f .env ]; then
    echo "❌ .env fayl topilmadi!"
    echo "📝 .env yaratish:"
    cp env_test_example.txt .env
    echo "✅ .env fayl yaratildi. Endi BOT_TOKEN va SUPER_ADMIN_IDS ni to'ldiring:"
    echo "nano .env"
    exit 1
fi

# Virtual environment
source venv/bin/activate

# SQLite uchun migratsiya
echo "🗄️ SQLite database yaratish..."
python manage.py migrate --run-syncdb

echo "✅ Database tayyor!"

# Django serverni background da ishga tushirish
echo "🚀 Django server..."
python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &
DJANGO_PID=$!

# Serverning ishga tushishini kutish
sleep 5

echo "🤖 Bot ishga tushirilmoqda..."
cd bot
python bot.py &
BOT_PID=$!

echo "✅ Hammasi tayyor!"
echo "📊 Django Admin: http://localhost:8000/admin/"
echo "🔗 API: http://localhost:8000/api/"
echo "🤖 Botga /start yuboring"
echo ""
echo "⏹️ To'xtatish: Ctrl+C"

# Signal handler
trap 'echo "🛑 To'\''xtatilmoqda..."; kill $DJANGO_PID $BOT_PID 2>/dev/null; exit' INT

# Kutish
wait
