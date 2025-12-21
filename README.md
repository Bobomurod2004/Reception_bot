# 🤖 Telegram Support Bot + Django Backend

Professional support-ticket tizimi - Telegram bot orqali foydalanuvchilar savol yuboradi, adminlar kategoriya bo'yicha javob beradi, super admin esa barcha jarayonni boshqaradi.

## 🏗️ Arxitektura

```
Telegram User/Admin → Aiogram Bot → Django REST API → PostgreSQL
```

**Asosiy prinsip:**
- Telegram Bot → faqat UI
- Django → business logic + DB + API  
- Bot va Django → faqat REST API orqali bog'lanadi

## 👥 Rollar

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

## 🚀 O'rnatish

### 1. Django Backend

```bash
# Virtual environment yaratish
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows

# Dependencies o'rnatish
pip install -r req.txt

# Database migratsiyalari
python manage.py makemigrations
python manage.py migrate

# Super user yaratish
python manage.py createsuperuser

# Serverni ishga tushirish
python manage.py runserver
```

### 2. Telegram Bot

```bash
# Bot dependencies o'rnatish
pip install -r bot_requirements.txt

# .env fayl yaratish
cp .env.example .env
# .env faylni to'ldiring

# Botni ishga tushirish
cd bot
python bot.py
```

## ⚙️ Konfiguratsiya

### .env fayl:

```env
# Bot konfiguratsiyasi
BOT_TOKEN=your_telegram_bot_token_here
DJANGO_API_URL=http://localhost:8000/api
API_TOKEN=your_api_token_here

# Super admin Telegram ID-lari
SUPER_ADMIN_IDS=123456789,987654321

# Logging
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

## 📊 API Endpoint-lar

### User API
- `GET /api/user/users/` - User list
- `POST /api/user/users/` - User yaratish
- `GET /api/user/users/{id}/` - User olish

### Ticket API
- `GET /api/ticket/tickets/` - Ticket list
- `POST /api/ticket/tickets/` - Ticket yaratish
- `GET /api/ticket/tickets/my-tickets/?admin_id=1` - Admin ticketlari
- `GET /api/ticket/tickets/user-tickets/?user_id=1` - User ticketlari
- `POST /api/ticket/tickets/{id}/assign-admin/` - Admin biriktirish
- `POST /api/ticket/tickets/{id}/close/` - Ticket yopish

### Message API
- `GET /api/ticket/messages/` - Message list
- `POST /api/ticket/messages/` - Message yaratish

### Admin API
- `GET /api/admin/admins/` - Admin list
- `POST /api/admin/admins/` - Admin yaratish
- `GET /api/admin/categories/` - Category list
- `POST /api/admin/categories/` - Category yaratish

## 🔄 User Flow

1. `/start` - Bot ishga tushadi
2. Kategoriya tanlash
3. Ochiq ticket bormi tekshirish (API)
4. Savol yozish
5. Ticket yaratildi
6. Admin javobi

## 🔄 Admin Flow

1. `/admin` - Admin rejimi
2. Mening ticketlarim
3. Ticket tanlash  
4. Javob yozish
5. Userga yuborildi

## 📎 Media Qo'llab-quvvatlash

- ✅ Text
- ✅ Image  
- ✅ Video
- ✅ Audio
- ✅ File (PDF va boshqalar)
- ✅ Location

## 🔐 Xavfsizlik

- Bot → Django: API Token
- User identifikatsiyasi: Telegram ID
- Admin role: Django orqali
- Permissionlar faqat backendda

## 📈 Xususiyatlar

### ✅ Tayyor
- Django REST API
- Admin assign logikasi
- Telegram Bot (User, Admin, Super Admin)
- FSM (Finite State Machine)
- Keyboard-lar
- Middleware (Auth)
- API Client service

### 🔄 Keyingi bosqichlar
- Media file handling
- Audit va loglar
- Hisobotlar
- Production deployment
- Redis cache
- Webhook mode

## 🗂️ Fayl Strukturasi

```
Django-Bot/
├── apps/
│   ├── admin/          # Admin modeli va API
│   ├── ticket/         # Ticket va Message modellari
│   └── user/           # User modeli
├── bot/
│   ├── config.py       # Bot konfiguratsiyasi
│   ├── bot.py          # Asosiy bot fayli
│   ├── services/
│   │   └── api.py      # Django API client
│   ├── routers/
│   │   ├── user.py     # User handlers
│   │   ├── admin.py    # Admin handlers
│   │   └── super_admin.py # Super admin handlers
│   ├── keyboards/
│   │   ├── user.py     # User keyboards
│   │   └── admin.py    # Admin keyboards
│   ├── fsm/
│   │   └── states.py   # FSM states
│   └── middlewares/
│       └── auth.py     # Auth middleware
├── core/               # Django settings
├── manage.py
├── req.txt            # Django requirements
└── bot_requirements.txt # Bot requirements
```

## 🚀 Production

### Docker (kelgusida)
```dockerfile
# Django
FROM python:3.11-slim
# Bot
FROM python:3.11-slim
```

### Nginx + Gunicorn
```nginx
server {
    listen 80;
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

## 📞 Qo'llab-quvvatlash

Savollar bo'lsa, issue yarating yoki bog'laning.

---

**Status: ✅ TAYYOR - Production uchun**
