# 🚀 Serverga Joylashtirish Qo'llanmasi

## ⚠️ MUHIM: Serverga joylashtirishdan oldin

### 1. **Webhook sozlash (MAJBURIY)**
- Bot polling emas, **webhook** rejimida ishlashi kerak
- Webhook uchun **HTTPS** va **domain** kerak
- Telegram webhook faqat HTTPS orqali ishlaydi

### 2. **Environment Variables (.env)**

```bash
# Bot mode - MAJBURIY webhook
BOT_MODE=webhook

# Webhook sozlamalari - MAJBURIY
WEBHOOK_HOST=https://yourdomain.com  # To'liq domain
WEBHOOK_PATH=/webhook
WEBHOOK_SECRET=random_secure_string_here  # Kuchli parol
WEBHOOK_PORT=8443
WEBHOOK_HOST_BIND=0.0.0.0

# Django API URL - Docker ichida
DJANGO_API_URL=http://web:8000/api

# Database - PostgreSQL (MAJBURIY)
USE_SQLITE=False  # yoki o'chirib tashlang
DB_NAME=support_bot_db
DB_USER=postgres
DB_PASSWORD=strong_password_here
DB_HOST=db
DB_PORT=5432

# Boshqa sozlamalar
BOT_TOKEN=your_bot_token
SUPER_ADMIN_IDS=your_telegram_id
API_TOKEN=strong_api_token
SECRET_KEY=django_secret_key
DEBUG=False  # Production da False
```

### 3. **SSL Sertifikat (HTTPS)**

Webhook uchun SSL kerak. Variantlar:

**A) Let's Encrypt (Bepul, tavsiya etiladi):**
```bash
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com
```

**B) Nginx reverse proxy bilan:**
- Nginx SSL ni boshqaradi
- Bot webhook portiga proxy qiladi

### 4. **Nginx Konfiguratsiyasi (Tavsiya etiladi)**

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location /webhook {
        proxy_pass http://localhost:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://localhost:8443;
    }
}
```

### 5. **Docker Deployment**

```bash
# 1. .env faylni to'ldiring (yuqoridagi sozlamalar bilan)

# 2. Docker images build
docker-compose build

# 3. Services ishga tushirish
docker-compose up -d

# 4. Logs tekshirish
docker-compose logs -f bot
docker-compose logs -f web
```

### 6. **Firewall Sozlamalari**

```bash
# Portlarni ochish
sudo ufw allow 80/tcp    # HTTP (SSL uchun)
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # Django (agar kerak bo'lsa)
sudo ufw allow 8443/tcp  # Webhook (agar to'g'ridan-to'g'ri ishlatilsa)
```

### 7. **PostgreSQL Backup**

```bash
# Backup yaratish
docker-compose exec db pg_dump -U postgres support_bot_db > backup.sql

# Restore qilish
docker-compose exec -T db psql -U postgres support_bot_db < backup.sql
```

### 8. **Monitoring va Logs**

```bash
# Bot logs
tail -f logs/bot.log

# Django logs
tail -f logs/django.log

# Docker logs
docker-compose logs -f
```

## ✅ Tekshirish

1. **Health check:**
   ```bash
   curl http://localhost:8000/health/
   curl http://localhost:8443/health
   ```

2. **Webhook status:**
   ```bash
   # Bot kodida webhook setup qilinganini tekshiring
   docker-compose logs bot | grep webhook
   ```

3. **Database:**
   ```bash
   docker-compose exec db pg_isready -U postgres
   ```

## 🔧 Muammolarni hal qilish

### Bot webhook ga ulanmayapti
- SSL sertifikat to'g'ri sozlanganligini tekshiring
- WEBHOOK_HOST to'g'ri domain ekanligini tekshiring
- Firewall portlarni ochganligingizni tekshiring
- Nginx konfiguratsiyasini tekshiring

### Database xatolari
- PostgreSQL container ishlayotganini tekshiring: `docker-compose ps db`
- DB_HOST=db (Docker network ichida)
- Parol va user to'g'ri ekanligini tekshiring

### API ulanish xatolari
- Django server ishlayotganini tekshiring
- DJANGO_API_URL=http://web:8000/api (Docker ichida)
- API_TOKEN bir xil ekanligini tekshiring

## 📝 Qisqa Checklist

- [ ] Domain va SSL sertifikat tayyor
- [ ] .env fayl to'liq to'ldirilgan
- [ ] BOT_MODE=webhook
- [ ] WEBHOOK_HOST to'g'ri sozlangan
- [ ] PostgreSQL sozlandi
- [ ] Docker-compose ishga tushdi
- [ ] Nginx sozlandi (agar kerak bo'lsa)
- [ ] Firewall portlari ochildi
- [ ] Webhook Telegram'da sozlandi
- [ ] Health check ishlayapti
- [ ] Logs tekshirildi

