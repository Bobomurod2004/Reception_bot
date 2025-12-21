from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.api import api_client
from config import SUPER_ADMIN_IDS

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """Foydalanuvchi autentifikatsiyasi va ro'yxatdan o'tkazish middleware"""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user = event.from_user

        # User ma'lumotlarini olish yoki yaratish
        db_user = await api_client.get_user_by_telegram_id(user.id)

        if not db_user:
            # Yangi user yaratish
            db_user = await api_client.create_user(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )

            if db_user and isinstance(db_user, dict):
                logger.info(
                    f"Yangi user yaratildi: {user.id},"
                    f" DB ID: {db_user.get('id', 'N/A')}")
            else:
                logger.error(
                    f"User yaratib bo'lmadi: {user.id},Response: {db_user}")
                # User yaratilmasa ham davom etish
                #  (faqat telegram ma'lumotlari bilan)
                db_user = {
                    'id': None,
                    'telegram_id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }

        # User ma'lumotlarini data ga qo'shish
        data['db_user'] = db_user

        # Language olish (default: None - til tanlatish uchun)
        user_language = None
        if db_user and isinstance(db_user, dict):
            user_language = db_user.get('language')
            # Agar language None yoki bo'sh bo'lsa, None qaytarish (til tanlatish uchun)
            if user_language and user_language not in ['uz', 'ru', 'en']:
                user_language = None
        data['user_language'] = user_language

        # Super admin ekanligini tekshirish (birinchi)
        data['is_super_admin'] = user.id in SUPER_ADMIN_IDS

        # Admin ekanligini tekshirish (faqat super admin bo'lmasa)
        admin = None
        if not data['is_super_admin'] and db_user and isinstance(db_user, dict) and 'id' in db_user:
            admin = await api_client.get_admin_by_user_id(db_user['id'])
        data['admin'] = admin

        # Role aniqlash (to'g'ri tartibda)
        if data['is_super_admin']:
            data['user_role'] = 'super_admin'
        elif admin and not admin.get('is_blocked'):
            data['user_role'] = 'admin'
        else:
            data['user_role'] = 'user'

        logger.debug(f"User {user.id} role: {data['user_role']}")

        return await handler(event, data)
