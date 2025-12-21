"""
i18n middleware for Aiogram
Sets locale based on user's language from database
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import I18n, I18nMiddleware, SimpleI18nMiddleware
from aiogram.utils.i18n.middleware import I18nMiddleware as BaseI18nMiddleware
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

# i18n instance yaratish
import pathlib
BASE_DIR = pathlib.Path(__file__).parent.parent
i18n = I18n(path=str(BASE_DIR / "locales"), default_locale="uz", domain="bot")

# Locale resolver - user language ni DB dan oladi
class DatabaseI18nMiddleware(BaseI18nMiddleware):
    """Database dan til olish middleware"""
    
    async def get_locale(self, event: Message | CallbackQuery, data: Dict[str, Any]) -> str:
        """User tilini DB dan olish"""
        # AuthMiddleware dan user_language ni olish
        user_language = data.get('user_language')

        # Agar user language None bo'lsa (til tanlanmagan), default 'uz' ishlatish
        if not user_language or user_language not in ['uz', 'ru', 'en']:
            user_language = 'uz'

        logger.debug(f"User {event.from_user.id} language: {user_language}")
        return user_language

# Middleware instance
i18n_middleware = DatabaseI18nMiddleware(i18n=i18n)

