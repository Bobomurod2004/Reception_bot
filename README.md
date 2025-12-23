# 🤖 Telegram Support Bot + Django Backend

Production-ready support-ticket system - Telegram bot orqali foydalanuvchilar savol yuboradi, adminlar kategoriya bo'yicha javob beradi, super admin esa barcha jarayonni boshqaradi.

## 🏗️ Architecture

```
Telegram User/Admin → Aiogram Bot (Webhook) → Django REST API → PostgreSQL
```

**Key Features:**
- ✅ **Webhook mode** (production-ready, no polling)
- ✅ **Fully async** (no blocking operations)
- ✅ **PostgreSQL** database (production)
- ✅ **Docker & docker-compose** deployment
- ✅ **Proper logging** with rotation
- ✅ **Optimized API client** with session reuse
- ✅ **Health checks** for monitoring

## 👥 Roles

### 👤 User
- Botni ishga tushiradi
- Kategoriya tanlaydi
- 1 ta ochiq ticket ochadi
- Xabarlar (text, video, audio, file, location) yuboradi
- Admin javoblarini oladi

### 👨‍💼 Admin  
- O'ziga biriktirilgan kategoriyalardagi ticketlarni ko'radi
- Ticketlarga javob beradi
- Ticket yopadi
- O'z faoliyatini ko'ra oladi

### 👑 Super Admin
- Barcha ticketlarni ko'radi
- Adminlarni va kategoriyalarni boshqaradi
- Hisobotlarni ko'radi
- Tizimni to'liq boshqaradi

## 🚀 Quick Start

### Local Testing (SQLite, Polling)

```bash
# 1. Clone repository
git clone https://github.com/Bobomurod2004/Reception_bot.git
cd Reception_bot

# 2. Create .env file
cp env_example.txt .env
# Edit .env and set BOT_TOKEN and SUPER_ADMIN_IDS

# 3. Run test script
chmod +x test_local.sh
./test_local.sh
```

### Production Deployment (Docker, PostgreSQL, Webhook)

```bash
# 1. Configure .env
cp env_example.txt .env
# Edit .env:
#   - Set BOT_TOKEN
#   - Set SUPER_ADMIN_IDS
#   - Set BOT_MODE=webhook
#   - Set WEBHOOK_HOST=https://yourdomain.com
#   - Set WEBHOOK_SECRET (random secure string)
#   - Configure database credentials

# 2. Deploy
chmod +x deploy_production.sh
./deploy_production.sh
```

## ⚙️ Configuration

### Environment Variables (.env)

**Required:**
- `BOT_TOKEN` - Telegram bot token from @BotFather
- `SUPER_ADMIN_IDS` - Comma-separated Telegram user IDs
- `API_TOKEN` - Secret token for bot-API communication
- `SECRET_KEY` - Django secret key

**Bot Mode:**
- `BOT_MODE=polling` - For local development
- `BOT_MODE=webhook` - For production (requires WEBHOOK_HOST)

**Webhook (Production):**
- `WEBHOOK_HOST=https://yourdomain.com`
- `WEBHOOK_PATH=/webhook`
- `WEBHOOK_SECRET=your_secret_token`
- `WEBHOOK_PORT=8443`

**Database:**
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- Or set `USE_SQLITE=True` for local testing

See `env_example.txt` for all options.

## 🐳 Docker Deployment

### Services

- **db** - PostgreSQL database
- **web** - Django REST API (Gunicorn)
- **bot** - Telegram bot (Webhook/Polling)

### Commands

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild
docker-compose build --no-cache
```

## 📊 API Endpoints

- `GET /health/` - Health check
- `GET /admin/` - Django admin panel
- `GET /api/user/users/` - User API
- `GET /api/admin/` - Admin API
- `GET /api/ticket/` - Ticket API

## 🔧 Development

### Project Structure

```
.
├── bot/              # Telegram bot (Aiogram)
│   ├── bot.py        # Main bot entry point
│   ├── webhook.py    # Webhook setup
│   ├── routers/      # Bot handlers
│   ├── services/     # API client
│   └── middlewares/  # Auth, i18n
├── apps/             # Django apps
│   ├── user/        # User management
│   ├── admin/       # Admin management
│   └── ticket/      # Ticket system
├── core/            # Django settings
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

### Key Improvements

1. **Webhook instead of Polling** - Production-ready, scalable
2. **Optimized API Client** - Reuses aiohttp session, connection pooling
3. **Proper Logging** - File rotation, structured logs
4. **PostgreSQL** - Production database
5. **Health Checks** - Docker health monitoring
6. **Error Handling** - Retry logic, timeouts
7. **No Blocking** - Fully async operations

## 🐛 Troubleshooting

### Bot not responding
- Check logs: `docker-compose logs bot`
- Verify BOT_TOKEN in .env
- Check webhook URL (if webhook mode)

### Database connection errors
- Verify DB credentials in .env
- Check if PostgreSQL is running: `docker-compose ps db`
- Check connection: `docker-compose exec db pg_isready`

### API connection errors
- Verify DJANGO_API_URL in .env
- Check web service: `docker-compose logs web`
- Test health endpoint: `curl http://localhost:8000/health/`

## 📝 License

MIT License

## 🔗 Links

- Repository: https://github.com/Bobomurod2004/Reception_bot
- Django Admin: http://localhost:8000/admin/ (after deployment)
