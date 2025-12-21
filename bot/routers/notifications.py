"""
Bot notification handlers - Django'dan kelgan real-time xabarlar
"""
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Bot

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.api import api_client
from keyboards.admin import get_ticket_admin_actions_keyboard
from aiogram.utils.i18n import gettext as _
from middlewares.i18n import i18n

logger = logging.getLogger(__name__)
router = Router()


async def notify_admin_new_ticket(bot: Bot, admin_telegram_id: int, ticket_id: int):
    """Admin'ga yangi ticket haqida xabar yuborish"""
    try:
        # Ticket ma'lumotlarini olish
        ticket = await api_client.get_ticket(ticket_id)
        if not ticket:
            logger.error(f"Ticket {ticket_id} topilmadi")
            return
        
        # Ticket xabarlarini olish
        messages = await api_client.get_ticket_messages(ticket_id)
        if not messages:
            logger.error(f"Ticket {ticket_id} uchun xabarlar topilmadi")
            return
        
        # Birinchi xabarni olish (user savoli)
        first_message = messages[0] if messages else None
        if not first_message:
            return
        
        # Ticket ma'lumotlarini tayyorlash
        ticket_number = ticket.get('ticket_number', f"#{ticket_id}")
        category_name = ticket.get('category', {}).get('name', 'Noma\'lum') if isinstance(ticket.get('category'), dict) else 'Noma\'lum'
        user_name = ticket.get('user', {}).get('first_name', 'Foydalanuvchi') if isinstance(ticket.get('user'), dict) else 'Foydalanuvchi'
        
        # Xabar matni
        content = first_message.get('content', '')
        content_type = first_message.get('content_type', 'text')
        file_id = first_message.get('file')
        
        # Admin tilini aniqlash
        admin_data = await api_client.get_user_by_telegram_id(admin_telegram_id)
        admin_lang = admin_data.get('language', 'uz') if admin_data else 'uz'
        
        with i18n.use_locale(admin_lang):
            # Xabar matni
            text = (
                f"🆕 **{_('admin_new_ticket_notification')}**\n\n"
                f"📋 {_('ticket_label')}: `{ticket_number}`\n"
                f"📁 {_('category_label')}: {category_name}\n"
                f"👤 {_('user_label')}: {user_name}\n"
                f"📝 {_('question_label')}:\n\n"
            )
            
            # Media sarlavhalari uchun tarjimalar
            img_caption = _("admin_sent_image")
            vid_caption = _("admin_sent_video")
            aud_caption = _("admin_sent_audio")
            file_caption = _("admin_sent_file")
        
        # Media yuborish
            if content_type == 'image' and file_id:
                await bot.send_photo(
                    chat_id=admin_telegram_id,
                    photo=file_id,
                    caption=text + (content or img_caption),
                    reply_markup=get_ticket_admin_actions_keyboard(ticket_id),
                    parse_mode='Markdown'
                )
            elif content_type == 'video' and file_id:
                await bot.send_video(
                    chat_id=admin_telegram_id,
                    video=file_id,
                    caption=text + (content or vid_caption),
                    reply_markup=get_ticket_admin_actions_keyboard(ticket_id),
                    parse_mode='Markdown'
                )
            elif content_type == 'audio' and file_id:
                await bot.send_audio(
                    chat_id=admin_telegram_id,
                    audio=file_id,
                    caption=text + (content or aud_caption),
                    reply_markup=get_ticket_admin_actions_keyboard(ticket_id),
                    parse_mode='Markdown'
                )
            elif content_type == 'file' and file_id:
                await bot.send_document(
                    chat_id=admin_telegram_id,
                    document=file_id,
                    caption=text + (content or file_caption),
                    reply_markup=get_ticket_admin_actions_keyboard(ticket_id),
                    parse_mode='Markdown'
                )
            elif content_type == 'location':
                # Location uchun latitude/longitude olish
                if content and 'Latitude:' in content:
                    try:
                        parts = content.split('\n')
                        lat = float(parts[0].split(':')[1].strip())
                        lon = float(parts[1].split(':')[1].strip())
                        await bot.send_location(
                            chat_id=admin_telegram_id,
                            latitude=lat,
                            longitude=lon
                        )
                        await bot.send_message(
                            chat_id=admin_telegram_id,
                            text=text + content,
                            reply_markup=get_ticket_admin_actions_keyboard(ticket_id),
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Location parse xatosi: {e}")
                        await bot.send_message(
                            chat_id=admin_telegram_id,
                            text=text + content,
                            reply_markup=get_ticket_admin_actions_keyboard(ticket_id),
                            parse_mode='Markdown'
                        )
                else:
                    await bot.send_message(
                        chat_id=admin_telegram_id,
                        text=text + content,
                        reply_markup=get_ticket_admin_actions_keyboard(ticket_id),
                        parse_mode='Markdown'
                    )
            else:
                # Oddiy text xabar
                await bot.send_message(
                    chat_id=admin_telegram_id,
                    text=text + (content or _("message_sent")),
                    reply_markup=get_ticket_admin_actions_keyboard(ticket_id),
                    parse_mode='Markdown'
                )
        
        logger.info(f"Admin {admin_telegram_id} ga yangi ticket {ticket_id} haqida xabar yuborildi")
        
    except Exception as e:
        logger.error(f"Admin'ga xabar yuborishda xatolik: {e}", exc_info=True)


async def notify_user_admin_replied(bot: Bot, user_telegram_id: int, ticket_id: int):
    """User'ga admin javobi haqida xabar yuborish"""
    try:
        # Ticket ma'lumotlarini olish
        ticket = await api_client.get_ticket(ticket_id)
        if not ticket:
            return
        
        # Oxirgi admin javobini olish
        messages = await api_client.get_ticket_messages(ticket_id)
        if not messages:
            return
        
        # Admin javobini topish (oxirgi admin xabari)
        admin_message = None
        for msg in reversed(messages):
            if msg.get('sender_admin'):
                admin_message = msg
                break
        
        if not admin_message:
            return
        
        # Admin javobi ma'lumotlari
        content = admin_message.get('content', '')
        content_type = admin_message.get('content_type', 'text')
        file_id = admin_message.get('file')
        
        # User tilini aniqlash
        user_data = await api_client.get_user_by_telegram_id(user_telegram_id)
        user_lang = user_data.get('language', 'uz') if user_data else 'uz'
        
        with i18n.use_locale(user_lang):
            text = f"✅ **{_('admin_replied_notification')}**\n\n"
            
            img_caption = _("admin_sent_image")
            vid_caption = _("admin_sent_video")
            aud_caption = _("admin_sent_audio")
            file_caption = _("admin_sent_file")
            msg_sent = _("message_sent")
        
            # Media yuborish
            if content_type == 'image' and file_id:
                await bot.send_photo(
                    chat_id=user_telegram_id,
                    photo=file_id,
                    caption=text + (content or img_caption),
                    parse_mode='Markdown'
                )
            elif content_type == 'video' and file_id:
                await bot.send_video(
                    chat_id=user_telegram_id,
                    video=file_id,
                    caption=text + (content or vid_caption),
                    parse_mode='Markdown'
                )
            elif content_type == 'audio' and file_id:
                await bot.send_audio(
                    chat_id=user_telegram_id,
                    audio=file_id,
                    caption=text + (content or aud_caption),
                    parse_mode='Markdown'
                )
            elif content_type == 'file' and file_id:
                await bot.send_document(
                    chat_id=user_telegram_id,
                    document=file_id,
                    caption=text + (content or file_caption),
                    parse_mode='Markdown'
                )
            elif content_type == 'location':
                if content and 'Latitude:' in content:
                    try:
                        parts = content.split('\n')
                        lat = float(parts[0].split(':')[1].strip())
                        lon = float(parts[1].split(':')[1].strip())
                        await bot.send_location(
                            chat_id=user_telegram_id,
                            latitude=lat,
                            longitude=lon
                        )
                        await bot.send_message(
                            chat_id=user_telegram_id,
                            text=text + content,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Location parse xatosi: {e}")
                        await bot.send_message(
                            chat_id=user_telegram_id,
                            text=text + content,
                            parse_mode='Markdown'
                        )
                else:
                    await bot.send_message(
                        chat_id=user_telegram_id,
                        text=text + content,
                        parse_mode='Markdown'
                    )
            else:
                await bot.send_message(
                    chat_id=user_telegram_id,
                    text=text + (content or msg_sent),
                    parse_mode='Markdown'
                )
        
        logger.info(f"User {user_telegram_id} ga admin javobi haqida xabar yuborildi")
        
    except Exception as e:
        logger.error(f"User'ga xabar yuborishda xatolik: {e}", exc_info=True)

