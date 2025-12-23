#!/usr/bin/env python3
"""
Local test script for bot - polling mode
Test qilish uchun ishlatish mumkin
"""
import sys
import os

# Bot papkasiga path qo'shish
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bot'))

# Environment o'zgaruvchilarini sozlash
os.environ.setdefault('BOT_TOKEN', '8508409899:AAEkEGhPFneERntm-F0Fz9N8P-yDAMclWWc')
os.environ.setdefault('USE_WEBHOOK', 'false')
os.environ.setdefault('REDIS_URL', 'redis://localhost:6380')
os.environ.setdefault('DJANGO_API_URL', 'http://localhost:8001/api')
os.environ.setdefault('LOG_LEVEL', 'INFO')

if __name__ == '__main__':
    print("=" * 50)
    print("Bot Test Script")
    print("=" * 50)
    print("\n1. Config import test...")
    
    try:
        from bot.config import BOT_TOKEN, USE_WEBHOOK, REDIS_URL
        print(f"   ✓ BOT_TOKEN: {BOT_TOKEN[:10]}...")
        print(f"   ✓ USE_WEBHOOK: {USE_WEBHOOK}")
        print(f"   ✓ REDIS_URL: {REDIS_URL}")
    except Exception as e:
        print(f"   ✗ Config import xatosi: {e}")
        sys.exit(1)
    
    print("\n2. Bot import test...")
    try:
        from bot.bot import bot, dp
        print(f"   ✓ Bot va Dispatcher yaratildi")
    except Exception as e:
        print(f"   ✗ Bot import xatosi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n3. API Client test...")
    try:
        from bot.services.api import api_client
        print(f"   ✓ API Client yaratildi")
    except Exception as e:
        print(f"   ✗ API Client xatosi: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("Test yakunlandi!")
    print("Botni ishga tushirish uchun: python bot/bot.py")
    print("=" * 50)

