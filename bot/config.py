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
