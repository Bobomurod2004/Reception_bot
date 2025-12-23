import os
from dotenv import load_dotenv

load_dotenv()

# Bot konfiguratsiyasi
BOT_TOKEN = os.getenv('BOT_TOKEN', 'PASTE_YOUR_TOKEN_HERE')
DJANGO_API_URL = os.getenv('DJANGO_API_URL', 'http://localhost:8000/api')
API_TOKEN = os.getenv('API_TOKEN', 'your-api-token')

# Admin konfiguratsiyasi
SUPER_ADMIN_IDS = [
    int(x) for x in os.getenv('SUPER_ADMIN_IDS', '').split(',') if x.strip()
]

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_DIR = os.getenv('LOG_DIR', 'logs')

# Webhook konfiguratsiyasi (production uchun)
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST', '')  # https://yourdomain.com
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH', '/webhook')
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}" if WEBHOOK_HOST else None
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')  # Webhook secret key

# Bot mode: 'polling' yoki 'webhook'
BOT_MODE = os.getenv('BOT_MODE', 'polling').lower()

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/dbname')

# Media
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_FILE_TYPES = [
    'image/jpeg', 'image/png', 'image/gif',
    'video/mp4', 'video/avi',
    'audio/mpeg', 'audio/wav',
    'application/pdf', 'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

# API Client settings
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
API_MAX_RETRIES = int(os.getenv('API_MAX_RETRIES', '3'))
API_RETRY_DELAY = float(os.getenv('API_RETRY_DELAY', '1.0'))
