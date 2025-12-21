# flake8: noqa
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import BOT_TOKEN, LOG_LEVEL
from middlewares.auth import AuthMiddleware
from middlewares.i18n import i18n_middleware
from routers import user, admin, super_admin

# Logging sozlash
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot va Dispatcher yaratish
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def setup_bot():
    """Bot sozlash"""
    # Middleware-larni ro'yxatdan o'tkazish
    # 1. AuthMiddleware birinchi (user ma'lumotlarini olish uchun)
    # 2. i18n middleware ikkinchi (user language'ga qarab)
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    dp.message.middleware(i18n_middleware)
    dp.callback_query.middleware(i18n_middleware)
    
    # Router-larni ro'yxatdan o'tkazish
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(super_admin.router)
    
    logger.info("Bot sozlandi va tayyor!")


async def main():
    """Asosiy funksiya"""
    try:
        await setup_bot()
        logger.info("Bot ishga tushmoqda...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot ishga tushmadi: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
