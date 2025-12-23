#!/bin/bash
# Production deployment script

set -e

echo "🚀 Production Deployment Script"
echo "================================"

# .env fayl tekshirish
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Please create .env file from env_example.txt and configure it"
    exit 1
fi

# Docker tekshirish
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed"
    exit 1
fi

# Environment variables tekshirish
source .env

if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" == "1234567890:AAEhBOweik9ai2u5chjEMqDRNspnm4g4k" ]; then
    echo "❌ BOT_TOKEN must be set in .env"
    exit 1
fi

if [ -z "$SUPER_ADMIN_IDS" ]; then
    echo "❌ SUPER_ADMIN_IDS must be set in .env"
    exit 1
fi

# Webhook mode tekshirish
if [ "$BOT_MODE" == "webhook" ]; then
    if [ -z "$WEBHOOK_HOST" ] || [ "$WEBHOOK_HOST" == "https://yourdomain.com" ]; then
        echo "❌ WEBHOOK_HOST must be set for webhook mode"
        exit 1
    fi
    echo "✅ Webhook mode enabled: $WEBHOOK_HOST$WEBHOOK_PATH"
else
    echo "⚠️  Using polling mode (not recommended for production)"
fi

# Docker images build
echo "🔨 Building Docker images..."
docker-compose build

# Docker containers ishga tushirish
echo "🚀 Starting services..."
docker-compose up -d

# Status tekshirish
echo "⏳ Waiting for services to start..."
sleep 10

echo "📊 Service status:"
docker-compose ps

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Restart: docker-compose restart"
echo "   - Bot logs: docker-compose logs -f bot"
echo "   - Web logs: docker-compose logs -f web"
echo ""

