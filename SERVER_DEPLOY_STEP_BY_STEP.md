# 🚀 SERVERGA JOYLASHTIRISH - QADAMMA-QADAM QO'LLANMA

## 📋 TAYYORGARLIK

### Qadam 1: Serverga ulanish
```bash
ssh user@your-server-ip
# yoki
ssh user@your-domain.com
```

### Qadam 2: Kerakli dasturlarni o'rnatish
```bash
# Yangilash
sudo apt update && sudo apt upgrade -y

# Docker o'rnatish
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo systemctl start docker

# Git o'rnatish (agar yo'q bo'lsa)
sudo apt install git -y

# Nginx o'rnatish (webhook uchun)
sudo apt install nginx -y
```

---

## 📦 LOYIHANI YUKLASH

### Qadam 3: Loyihani serverga yuklash
```bash
# 1. Loyiha papkasiga o'tish
cd /opt  # yoki boshqa papka
# yoki
cd /home/your-user

# 2. Git orqali clone qilish
git clone https://github.com/Bobomurod2004/Reception_bot.git
cd Reception_bot

# YOKI agar fayllarni boshqa usul bilan yuklasangiz:
# scp orqali yuklash (local mashinadan):
# scp -r /path/to/Bot user@server:/opt/Reception_bot
```

---

## ⚙️ KONFIGURATSIYA

### Qadam 4: .env faylini yaratish va to'ldirish
```bash
# .env fayl yaratish
cp env_example.txt .env
nano .env  # yoki vim .env
```

**.env fayl ichida quyidagilarni to'ldiring:**

```bash
# ===== BOT SOZLAMALARI =====
BOT_TOKEN=8508409899:AAEkEGhPFneERntm-F0Fz9N8P-yDAMclWWc
BOT_MODE=webhook  # ⚠️ MAJBURIY: webhook bo'lishi kerak

# ===== WEBHOOK SOZLAMALARI =====
WEBHOOK_HOST=https://yourdomain.com  # ⚠️ O'zingizning domain nomingiz
WEBHOOK_PATH=/webhook
WEBHOOK_SECRET=my_very_secure_secret_token_12345  # ⚠️ Random kuchli parol
WEBHOOK_PORT=8443
WEBHOOK_HOST_BIND=0.0.0.0

# ===== DJANGO API =====
DJANGO_API_URL=http://web:8000/api  # Docker ichida

# ===== DATABASE (PostgreSQL) =====
USE_SQLITE=False  # ⚠️ False bo'lishi kerak
DB_NAME=support_bot_db
DB_USER=postgres
DB_PASSWORD=your_very_strong_password_here  # ⚠️ Kuchli parol
DB_HOST=db  # Docker ichida
DB_PORT=5432

# ===== ADMIN =====
SUPER_ADMIN_IDS=5652442685  # O'zingizning Telegram ID

# ===== API TOKEN =====
API_TOKEN=your_secure_api_token_here  # Bot va Django o'rtasida

# ===== DJANGO =====
SECRET_KEY=django-insecure-change-this-to-random-string  # ⚠️ Yangi random string
DEBUG=False  # ⚠️ Production da False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com  # ⚠️ O'zingizning domain

# ===== LOGGING =====
LOG_LEVEL=INFO
LOG_DIR=logs
```

**Muhim:** 
- `WEBHOOK_HOST` ga to'liq domain yozing: `https://example.com`
- `WEBHOOK_SECRET` ga random kuchli parol yozing
- `DB_PASSWORD` ga kuchli parol yozing
- `SECRET_KEY` ni yangi random string bilan almashtiring

---

## 🔒 SSL SERTIFIKAT (HTTPS)

### Qadam 5: Domain sozlash
```bash
# 1. Domain nomingizni server IP ga yo'naltiring (DNS)
# A record: yourdomain.com -> server-ip
# A record: www.yourdomain.com -> server-ip

# 2. DNS o'zgarishini kutish (5-30 minut)
# Tekshirish:
nslookup yourdomain.com
```

### Qadam 6: SSL sertifikat olish (Let's Encrypt)
```bash
# Certbot o'rnatish
sudo apt install certbot -y

# SSL sertifikat olish
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Sertifikatlar quyidagi joyda bo'ladi:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

**Eslatma:** Agar 80-port band bo'lsa, avval nginx ni to'xtating:
```bash
sudo systemctl stop nginx
sudo certbot certonly --standalone -d yourdomain.com
sudo systemctl start nginx
```

---

## 🌐 NGINX KONFIGURATSIYASI

### Qadam 7: Nginx sozlash
```bash
# Nginx konfiguratsiya faylini yaratish
sudo nano /etc/nginx/sites-available/bot.conf
```

**Quyidagi konfiguratsiyani yozing:**

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # HTTP dan HTTPS ga yo'naltirish
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL sertifikatlar
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL sozlamalari
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Webhook endpoint
    location /webhook {
        proxy_pass http://localhost:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8443;
        proxy_set_header Host $host;
    }

    # Django API (agar kerak bo'lsa)
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django Admin (agar kerak bo'lsa)
    location /admin/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Nginx ni faollashtirish:**
```bash
# Symlink yaratish
sudo ln -s /etc/nginx/sites-available/bot.conf /etc/nginx/sites-enabled/

# Default nginx config ni o'chirish (agar kerak bo'lsa)
sudo rm /etc/nginx/sites-enabled/default

# Konfiguratsiyani tekshirish
sudo nginx -t

# Nginx ni qayta ishga tushirish
sudo systemctl reload nginx
# yoki
sudo systemctl restart nginx
```

---

## 🔥 FIREWALL SOZLASH

### Qadam 8: Portlarni ochish
```bash
# Firewall holatini tekshirish
sudo ufw status

# Agar firewall o'chirilgan bo'lsa, yoqish
sudo ufw enable

# Portlarni ochish
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8443/tcp  # Webhook (agar to'g'ridan-to'g'ri ishlatilsa)

# Firewall holatini tekshirish
sudo ufw status
```

---

## 🐳 DOCKER DEPLOYMENT

### Qadam 9: Docker images build qilish
```bash
# Loyiha papkasiga o'tish
cd /opt/Reception_bot  # yoki qayerda yuklagan bo'lsangiz

# Docker images build
docker-compose build

# Bu biroz vaqt olishi mumkin (5-10 minut)
```

### Qadam 10: Services ishga tushirish
```bash
# Services ni background da ishga tushirish
docker-compose up -d

# Status tekshirish
docker-compose ps

# Logs tekshirish
docker-compose logs -f bot
docker-compose logs -f web
docker-compose logs -f db
```

**Agar xatolik bo'lsa:**
```bash
# Logs ni ko'rish
docker-compose logs

# Services ni to'xtatish
docker-compose down

# Qayta ishga tushirish
docker-compose up -d
```

---

## ✅ TEKSHIRISH

### Qadam 11: Barcha narsalarni tekshirish

**1. Database tekshirish:**
```bash
docker-compose exec db pg_isready -U postgres
# Natija: "postgresql://postgres@localhost:5432/postgres - accepting connections"
```

**2. Django health check:**
```bash
curl http://localhost:8000/health/
# Natija: {"status": "ok", "service": "django_api"}
```

**3. Bot health check:**
```bash
curl http://localhost:8443/health
# Natija: {"status": "ok", "service": "telegram_bot"}
```

**4. Webhook status:**
```bash
docker-compose logs bot | grep webhook
# "Webhook set successfully: https://yourdomain.com/webhook" ko'rinishi kerak
```

**5. HTTPS orqali tekshirish:**
```bash
curl https://yourdomain.com/health
# yoki brauzerda oching: https://yourdomain.com/health
```

**6. Bot logs:**
```bash
# Real-time logs
docker-compose logs -f bot

# Yoki fayldan
tail -f logs/bot.log
```

---

## 🔄 AUTOMATIC SSL RENEWAL

### Qadam 12: SSL sertifikatni avtomatik yangilash
```bash
# Certbot avtomatik renewal sozlash
sudo certbot renew --dry-run

# Crontab ga qo'shish (har oy avtomatik yangilash)
sudo crontab -e
# Quyidagi qatorni qo'shing:
0 0 1 * * certbot renew --quiet && systemctl reload nginx
```

---

## 📊 MONITORING

### Qadam 13: Monitoring sozlash

**Logs monitoring:**
```bash
# Bot logs
tail -f logs/bot.log

# Django logs
tail -f logs/django.log

# Docker logs
docker-compose logs -f
```

**System monitoring:**
```bash
# Docker containers status
docker-compose ps

# System resources
htop
# yoki
df -h  # Disk space
free -h  # RAM
```

---

## 🛠️ MUAMMOLARNI HAL QILISH

### Muammo 1: Bot webhook ga ulanmayapti
```bash
# 1. Webhook URL ni tekshirish
docker-compose logs bot | grep webhook

# 2. SSL sertifikatni tekshirish
sudo certbot certificates

# 3. Nginx konfiguratsiyasini tekshirish
sudo nginx -t

# 4. Portlarni tekshirish
sudo netstat -tlnp | grep 8443
```

### Muammo 2: Database ulanish xatosi
```bash
# 1. PostgreSQL container ishlayotganini tekshirish
docker-compose ps db

# 2. Database logs
docker-compose logs db

# 3. Database ga ulanish
docker-compose exec db psql -U postgres -d support_bot_db
```

### Muammo 3: Django ishlamayapti
```bash
# 1. Django logs
docker-compose logs web

# 2. Django container status
docker-compose ps web

# 3. Migrations tekshirish
docker-compose exec web python manage.py showmigrations
```

### Muammo 4: Port band
```bash
# Qaysi port band ekanligini ko'rish
sudo netstat -tlnp | grep :8443
sudo netstat -tlnp | grep :8000

# Process ni to'xtatish
sudo kill -9 <PID>
```

---

## 🔄 UPDATE QILISH

### Qadam 14: Loyihani yangilash
```bash
# 1. Git dan yangi versiyani olish
cd /opt/Reception_bot
git pull origin main

# 2. Docker images ni qayta build
docker-compose build

# 3. Services ni qayta ishga tushirish
docker-compose down
docker-compose up -d

# 4. Migrations (agar kerak bo'lsa)
docker-compose exec web python manage.py migrate
```

---

## 📝 YAKUNIY CHECKLIST

Deployment dan oldin tekshiring:

- [ ] Serverga ulanish muvaffaqiyatli
- [ ] Docker va docker-compose o'rnatilgan
- [ ] Nginx o'rnatilgan va sozlangan
- [ ] Domain DNS sozlangan
- [ ] SSL sertifikat olingan
- [ ] .env fayl to'liq to'ldirilgan
- [ ] BOT_MODE=webhook
- [ ] WEBHOOK_HOST to'g'ri sozlangan
- [ ] WEBHOOK_SECRET kuchli parol
- [ ] DB_PASSWORD kuchli parol
- [ ] DEBUG=False
- [ ] Firewall portlari ochilgan
- [ ] Docker-compose build muvaffaqiyatli
- [ ] Services ishga tushgan
- [ ] Health checks ishlayapti
- [ ] Webhook Telegram'da sozlangan
- [ ] Bot javob berayapti

---

## 🎉 TAYYOR!

Agar barcha qadamlarni to'g'ri bajarsangiz, bot serverda ishlayapti va webhook orqali Telegram dan xabarlarni qabul qilayapti!

**Foydali komandalar:**
```bash
# Services ni to'xtatish
docker-compose down

# Services ni qayta ishga tushirish
docker-compose restart

# Logs ko'rish
docker-compose logs -f

# Status
docker-compose ps
```

