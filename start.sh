#!/bin/bash

# Support Bot ishga tushirish skripti

echo "🤖 Support Bot ishga tushirilmoqda..."

# .env fayl mavjudligini tekshirish
if [ ! -f .env ]; then
    echo "❌ .env fayl topilmadi!"
    echo "📝 .env fayl yaratish:"
    echo "1. env_test_example.txt ni .env ga nusxalang:"
    echo "   cp env_test_example.txt .env"
    echo "2. .env faylini tahrirlang va o'z ma'lumotlaringizni kiriting"
    echo "3. BOT_TOKEN va SUPER_ADMIN_IDS ni to'ldiring"
    exit 1
fi

# Virtual environment faollashtirish
echo "📦 Virtual environment faollashtirish..."
source venv/bin/activate

# Django migratsiyalari
echo "🗄️ Database migratsiyalari..."
python manage.py makemigrations
python manage.py migrate

# Django serverni ishga tushirish (background)
echo "🚀 Django server ishga tushirilmoqda..."
python manage.py runserver &
DJANGO_PID=$!

# Serverning ishga tushishini kutish
sleep 3

# Bot dependencies o'rnatish
echo "📦 Bot dependencies o'rnatish..."
pip install -q -r bot_requirements.txt

# Locale fayllarini compile qilish
echo "🌐 Til fayllarini compile qilish..."
cd bot/locales
for lang in uz ru en; do
    msgfmt -o $lang/LC_MESSAGES/bot.mo $lang/LC_MESSAGES/bot.po 2>/dev/null || echo "⚠️ $lang compile qilishda xatolik"
done
cd ../..

# Botni ishga tushirish
echo "🤖 Telegram bot ishga tushirilmoqda..."
cd bot
python bot.py &
BOT_PID=$!
cd ..

echo "✅ Barcha servislar ishga tushdi!"
echo "📊 Django Admin: http://localhost:8000/admin/"
echo "🔗 API: http://localhost:8000/api/"
echo "🤖 Telegram botga /start yuboring"
echo ""
echo "⏹️ To'xtatish uchun Ctrl+C bosing"

# Signal handler
trap 'echo "🛑 Servislar toʻxtatilmoqda..."; kill $DJANGO_PID $BOT_PID; exit' INT

# Kutish
wait
