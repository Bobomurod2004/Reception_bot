#!/usr/bin/env python3
"""
Bot test skripti - API va bot komponentlarini test qilish
"""

import asyncio
import sys
import os

# Bot papkasini path ga qo'shish
bot_path = os.path.join(os.path.dirname(__file__), 'bot')
sys.path.append(bot_path)

from services.api import api_client

async def test_api():
    """API-larni test qilish"""
    print("🧪 API Test boshlandi...")
    
    try:
        # Categories test
        print("📂 Kategoriyalarni test qilish...")
        categories = await api_client.get_categories()
        print(f"✅ Kategoriyalar: {len(categories) if categories else 0} ta")
        
        # Test user yaratish
        print("👤 Test user yaratish...")
        test_user = await api_client.create_user(
            telegram_id=999999999,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        
        if test_user:
            print(f"✅ Test user yaratildi: ID {test_user.get('id')}")
            
            # User qidirish test
            found_user = await api_client.get_user_by_telegram_id(999999999)
            if found_user:
                print("✅ User qidirish ishlaydi")
            else:
                print("❌ User qidirish ishlamaydi")
        else:
            print("❌ Test user yaratilmadi")
            
    except Exception as e:
        print(f"❌ API Test xatosi: {e}")
    
    print("🧪 API Test tugadi")

async def main():
    """Asosiy test funksiya"""
    print("🚀 Bot Test Boshlandi")
    print("=" * 50)
    
    await test_api()
    
    print("=" * 50)
    print("✅ Test tugadi")

if __name__ == "__main__":
    asyncio.run(main())
