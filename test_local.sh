#!/bin/bash
# Local test script (SQLite, polling mode)

set -e

echo "🧪 Local Test Mode - Starting..."

# .env fayl yaratish yoki tekshirish
if [ ! -f .env ]; then
    echo "📝 Creating .env from env_example.txt..."
    cp env_example.txt .env
    echo "⚠️  Please edit .env and set BOT_TOKEN and SUPER_ADMIN_IDS"
    echo "   Then run this script again"
    exit 1
fi

# Local test uchun DJANGO_API_URL ni to'g'rilash
echo "🔧 Configuring .env for local test..."
if grep -q "DJANGO_API_URL=http://web:8000/api" .env; then
    sed -i 's|DJANGO_API_URL=http://web:8000/api|DJANGO_API_URL=http://localhost:8000/api|g' .env
    echo "✅ Updated DJANGO_API_URL to http://localhost:8000/api"
fi

# BOT_MODE ni polling ga o'rnatish
if ! grep -q "^BOT_MODE=" .env; then
    echo "BOT_MODE=polling" >> .env
elif grep -q "^BOT_MODE=webhook" .env; then
    sed -i 's/^BOT_MODE=webhook/BOT_MODE=polling/g' .env
    echo "✅ Updated BOT_MODE to polling"
fi

# USE_SQLITE ni tekshirish
if ! grep -q "^USE_SQLITE=True" .env; then
    if grep -q "^USE_SQLITE=" .env; then
        sed -i 's/^USE_SQLITE=.*/USE_SQLITE=True/g' .env
    else
        echo "USE_SQLITE=True" >> .env
    fi
    echo "✅ Set USE_SQLITE=True for local testing"
fi

# Virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

# Dependencies o'rnatish
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r bot_requirements.txt

# SQLite uchun sozlash
export USE_SQLITE=True
export BOT_MODE=polling

# Database migratsiyalari
echo "🗄️  Running migrations..."
python manage.py migrate

# Super user yaratish (agar yo'q bo'lsa)
echo "👤 Creating superuser (if needed)..."
python manage.py createsuperuser --noinput 2>/dev/null || echo "Superuser already exists or interactive mode required"

# Locale compile
echo "🌐 Compiling locales..."
cd bot/locales
for lang in uz ru en; do
    if [ -f "$lang/LC_MESSAGES/bot.po" ]; then
        msgfmt -o $lang/LC_MESSAGES/bot.mo $lang/LC_MESSAGES/bot.po 2>/dev/null || echo "⚠️  $lang compile error"
    fi
done
cd ../..

# Logs directory
mkdir -p logs

echo "✅ Setup complete!"
echo ""
echo "🚀 Starting services..."
echo "   - Django: http://localhost:8000"
echo "   - Admin: http://localhost:8000/admin"
echo "   - Bot: Polling mode"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Django background da
python manage.py runserver 0.0.0.0:8000 > logs/django_test.log 2>&1 &
DJANGO_PID=$!

# Kutish
sleep 3

# Bot foreground da
cd bot
python bot.py &
BOT_PID=$!
cd ..

# Signal handler
trap 'echo "🛑 Stopping..."; kill $DJANGO_PID $BOT_PID 2>/dev/null; exit' INT TERM

# Kutish
wait

