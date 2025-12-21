from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
import logging
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fsm.states import AdminStates
from keyboards.admin import (
    get_admin_main_menu_keyboard, get_admin_tickets_keyboard,
    get_ticket_admin_actions_keyboard, get_admin_cancel_keyboard
)
from keyboards.user import get_main_menu_keyboard, get_settings_keyboard
from keyboards.language import get_language_keyboard
from aiogram.utils.i18n import gettext as _
from middlewares.i18n import i18n
from services.api import api_client

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text.in_(["⚙️ Sozlamalar", "⚙️ Settings", "⚙️ Настройки"]))
async def admin_settings_menu(message: Message):
    """Admin sozlamalar menyusi"""
    await message.answer(
        _("settings_message"),
        reply_markup=get_settings_keyboard()
    )


@router.message(F.text.contains("Language") | F.text.contains("Til") | F.text.contains("Язык"))
async def admin_select_language(message: Message):
    """Admin til tanlash - Keng match"""
    logger.info(f"Admin language button pressed. Received text: '{message.text}'")
    
    if any(keyword in message.text for keyword in ["Language", "Til", "Язык"]):
        await message.answer(
            _("select_language"),
            reply_markup=get_language_keyboard()
        )


@router.message(F.text.in_(["📋 Mening ticketlarim", "📋 Мои тикеты", "📋 My tickets"]))
async def my_admin_tickets(message: Message, admin: dict, bot):
    """Admin o'z ticketlariga bugungi filtr bilan kirishi"""
    if not admin:
        await message.answer(_("admin_not_found"))
        return
    
    # Bugungi ticketlarni olish
    tickets = await api_client.get_admin_tickets(admin['id'], date_filter='today')
    
    # Ticketlarni ko'rsatish
    await message.answer(
        _("admin_my_tickets_count").format(count=len(tickets)),
        reply_markup=get_admin_tickets_keyboard(tickets, current_filter='today')
    )


@router.message(Command("admin"))
async def cmd_admin(message: Message, user_role: str, admin: dict, bot):
    """Admin rejimi - barcha savollarni ketma-ket ko'rsatish"""
    if user_role not in ['admin', 'super_admin']:
        await message.answer(_("no_admin_rights"))
        return
    
    if not admin:
        await message.answer(_("admin_profile_not_found"))
        return
    
    # Barcha kutayotgan savollarni olish (sana cheklovisiz)
    tickets = await api_client.get_admin_tickets(admin['id'], date_filter='all')
    
    if not tickets:
        await message.answer(
            _("admin_no_tickets")
        )
        return
    
    # Faqat kutayotgan va jarayondagi ticketlar
    waiting_tickets = [
        t for t in tickets 
        if t['status'] in ['waiting_admin', 'in_progress', 'open']
    ]
    
    # Admin javob bermagan savollarni filtrlash
    unanswered_tickets = []
    for ticket_data in waiting_tickets:
        # Ticket xabarlarini olish
        messages = await api_client.get_ticket_messages(ticket_data['id'])
        
        # Admin javobi borligini tekshirish
        has_admin_reply = False
        if messages:
            # Agar xabarlar ichida admin javobi bo'lsa
            for msg in messages:
                if msg.get('sender_admin') is not None and msg.get('sender_admin') != '':
                    has_admin_reply = True
                    break
        
        # Agar admin javob bermagan bo'lsa, ro'yxatga qo'shish
        if not has_admin_reply:
            unanswered_tickets.append(ticket_data)
    
    if not unanswered_tickets:
        await message.answer(
            _("all_questions_resolved") + "\n\n" + _("notified_on_new_questions")
        )
        return
    
    # Savollarni yaratilish vaqti bo'yicha tartiblash
    unanswered_tickets.sort(key=lambda x: x.get('created_at', ''))
    
    # Har bir savolni alohida xabar sifatida ko'rsatish (media bilan)
    for i, ticket_data in enumerate(unanswered_tickets, 1):
        ticket = await api_client.get_ticket(ticket_data['id'])
        if not ticket:
            continue
        
        # User ma'lumotlarini olish
        user_response = await api_client._make_request('GET', f"user/users/{ticket['user']}/")
        user_name = _("unknown")
        if user_response:
            user_name = f"{user_response.get('first_name', '')} {user_response.get('last_name', '')}".strip() or user_response.get('username', 'Noma\'lum')
        
        # Birinchi xabarni olish (media uchun)
        messages = await api_client.get_ticket_messages(ticket['id'])
        first_message = messages[0] if messages else None
        
        # Savol matni (qisqa va oddiy)
        priority_emoji = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🔴'
        }.get(ticket.get('priority', 'medium'), '🟡')
        
        created_time = ticket['created_at'][:16].replace('T', ' ')
        
        text = (
            f"👤 {user_name}\n"
            f"📝 {ticket['title']}\n"
            f"{priority_emoji} {ticket.get('priority', 'medium').title()}\n"
            f"📅 {created_time}\n"
            f"📋 {_('ticket_label')}: {ticket['ticket_number']}\n\n"
            f"💬 {ticket['description']}"
        )
        
        # Inline tugmalar
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("reply"),
                    callback_data=f"admin_reply_{ticket['id']}"
                ),
                InlineKeyboardButton(
                    text=_("close"),
                    callback_data=f"admin_close_no_reply_{ticket['id']}"
                )
            ]
        ])
        
        # Media bilan yuborish
        if first_message and first_message.get('file'):
            file_id = first_message.get('file')
            content_type = first_message.get('content_type', 'text')
            
            try:
                if content_type == "image":
                    await bot.send_photo(
                        chat_id=message.chat.id,
                        photo=file_id,
                        caption=text,
                        reply_markup=keyboard
                    )
                elif content_type == "video":
                    await bot.send_video(
                        chat_id=message.chat.id,
                        video=file_id,
                        caption=text,
                        reply_markup=keyboard
                    )
                elif content_type == "audio":
                    await bot.send_audio(
                        chat_id=message.chat.id,
                        audio=file_id,
                        caption=text,
                        reply_markup=keyboard
                    )
                elif content_type == "file":
                    await bot.send_document(
                        chat_id=message.chat.id,
                        document=file_id,
                        caption=text,
                        reply_markup=keyboard
                    )
                elif content_type == "location" and first_message.get('content'):
                    # Location xabarni ko'rsatish
                    # Location ma'lumotlarini parse qilish
                    location_text = first_message.get('content', '')
                    try:
                        # "📍 Joylashuv:\nLatitude: X\nLongitude: Y" formatidan parse qilish
                        if 'Latitude:' in location_text and 'Longitude:' in location_text:
                            lines = location_text.split('\n')
                            lat = None
                            lon = None
                            for line in lines:
                                if 'Latitude:' in line:
                                    lat = float(line.split('Latitude:')[1].strip())
                                elif 'Longitude:' in line:
                                    lon = float(line.split('Longitude:')[1].strip())
                            
                            if lat and lon:
                                await bot.send_location(
                                    chat_id=message.chat.id,
                                    latitude=lat,
                                    longitude=lon
                                )
                                await message.answer(text, reply_markup=keyboard)
                            else:
                                await message.answer(text, reply_markup=keyboard)
                        else:
                            await message.answer(text, reply_markup=keyboard)
                    except Exception as e:
                        logger.error(f"Location parse error: {e}")
                        await message.answer(text, reply_markup=keyboard)
                else:
                    await message.answer(text, reply_markup=keyboard)
            except Exception as e:
                logger.error(f"Media yuborishda xatolik: {e}")
                await message.answer(text, reply_markup=keyboard)
        else:
            await message.answer(text, reply_markup=keyboard)
        
        # Kichik kechikish (xabarlar ketma-ket ko'rinishi uchun)
        import asyncio
        if i < len(waiting_tickets):
            await asyncio.sleep(0.2)


async def show_next_ticket(message_or_callback, admin: dict, bot=None):
    """Keyingi kutayotgan savolni ko'rsatish (media bilan)"""
    tickets = await api_client.get_admin_tickets(admin['id'])
    
    if not tickets:
        return
    
    # Faqat kutayotgan va jarayondagi ticketlar
    waiting_tickets = [
        t for t in tickets 
        if t['status'] in ['waiting_admin', 'in_progress', 'open']
    ]
    
    if not waiting_tickets:
        return
    
    # Admin javob bermagan savollarni filtrlash
    unanswered_tickets = []
    for ticket_data in waiting_tickets:
        # Ticket xabarlarini olish
        messages = await api_client.get_ticket_messages(ticket_data['id'])
        
        # Admin javobi borligini tekshirish
        has_admin_reply = False
        if messages:
            # Agar xabarlar ichida admin javobi bo'lsa
            for msg in messages:
                if msg.get('sender_admin') is not None and msg.get('sender_admin') != '':
                    has_admin_reply = True
                    break
        
        # Agar admin javob bermagan bo'lsa, ro'yxatga qo'shish
        if not has_admin_reply:
            unanswered_tickets.append(ticket_data)
    
    if not unanswered_tickets:
        return
    
    # Eng eski savolni tanlash (birinchi kelgan)
    next_ticket = min(unanswered_tickets, key=lambda x: x.get('created_at', ''))
    
    # Ticket ma'lumotlarini olish
    ticket = await api_client.get_ticket(next_ticket['id'])
    if not ticket:
        return
    
    # User ma'lumotlarini olish
    user_response = await api_client._make_request('GET', f"user/users/{ticket['user']}/")
    user_name = _("unknown")
    if user_response:
        user_name = f"{user_response.get('first_name', '')} {user_response.get('last_name', '')}".strip() or user_response.get('username', 'Noma\'lum')
    
    # Birinchi xabarni olish (media uchun)
    messages = await api_client.get_ticket_messages(ticket['id'])
    first_message = messages[0] if messages else None
    
    # Savol matni (qisqa va oddiy)
    priority_emoji = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🔴'
    }.get(ticket.get('priority', 'medium'), '🟡')
    
    created_time = ticket['created_at'][:16].replace('T', ' ')
    
    text = (
        f"👤 {user_name}\n"
        f"📝 {ticket['title']}\n"
        f"{priority_emoji} {ticket.get('priority', 'medium').title()}\n"
        f"📅 {created_time}\n"
        f"📋 {_('ticket_label')}: {ticket['ticket_number']}\n\n"
        f"💬 {ticket['description']}"
    )
    
    # Inline tugmalar
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("reply"),
                callback_data=f"admin_reply_{ticket['id']}"
            ),
            InlineKeyboardButton(
                text=_("close"),
                callback_data=f"admin_close_no_reply_{ticket['id']}"
            )
        ]
    ])
    
    # Chat ID ni olish
    if isinstance(message_or_callback, Message):
        chat_id = message_or_callback.chat.id
        send_func = message_or_callback.answer
    else:
        chat_id = message_or_callback.message.chat.id
        send_func = message_or_callback.message.answer
    
    # Media bilan yuborish
    if first_message and first_message.get('file') and bot:
        file_id = first_message.get('file')
        content_type = first_message.get('content_type', 'text')
        
        try:
            if content_type == "image":
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=file_id,
                    caption=text,
                    reply_markup=keyboard
                )
            elif content_type == "video":
                await bot.send_video(
                    chat_id=chat_id,
                    video=file_id,
                    caption=text,
                    reply_markup=keyboard
                )
            elif content_type == "audio":
                await bot.send_audio(
                    chat_id=chat_id,
                    audio=file_id,
                    caption=text,
                    reply_markup=keyboard
                )
            elif content_type == "file":
                await bot.send_document(
                    chat_id=chat_id,
                    document=file_id,
                    caption=text,
                    reply_markup=keyboard
                )
            elif content_type == "location" and first_message.get('content'):
                # Location xabarni ko'rsatish
                location_text = first_message.get('content', '')
                try:
                    if 'Latitude:' in location_text and 'Longitude:' in location_text:
                        lines = location_text.split('\n')
                        lat = None
                        lon = None
                        for line in lines:
                            if 'Latitude:' in line:
                                lat = float(line.split('Latitude:')[1].strip())
                            elif 'Longitude:' in line:
                                lon = float(line.split('Longitude:')[1].strip())
                        
                        if lat and lon:
                            await bot.send_location(
                                chat_id=chat_id,
                                latitude=lat,
                                longitude=lon
                            )
                            await send_func(text, reply_markup=keyboard)
                        else:
                            await send_func(text, reply_markup=keyboard)
                    else:
                        await send_func(text, reply_markup=keyboard)
                except Exception as e:
                    logger.error(f"Location parse error: {e}")
                    await send_func(text, reply_markup=keyboard)
            else:
                await send_func(text, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Media yuborishda xatolik: {e}")
            await send_func(text, reply_markup=keyboard)
    else:
        await send_func(text, reply_markup=keyboard)
    
    if not isinstance(message_or_callback, Message):
        await message_or_callback.answer()


@router.callback_query(F.data.startswith("admin_ticket_"))
async def show_admin_ticket_details(callback: CallbackQuery, admin: dict):
    """Admin ticket tafsilotlari va xabarlar"""
    ticket_id = int(callback.data.split("_")[2])
    
    ticket = await api_client.get_ticket(ticket_id)
    if not ticket:
        await callback.answer(_("ticket_not_found"))
        return
    
    # Faqat o'z ticketini ko'ra oladi
    if ticket.get('assigned_admin') != admin['id']:
        await callback.answer(_("ticket_not_assigned"))
        return
    
    # Ticket xabarlarini olish
    messages = await api_client.get_ticket_messages(ticket_id)
    
    # User ma'lumotlarini olish
    user_response = await api_client._make_request('GET', f"user/users/{ticket['user']}/")
    user_name = _("unknown")
    if user_response:
        user_name = f"{user_response.get('first_name', '')} {user_response.get('last_name', '')}".strip() or user_response.get('username', 'Noma\'lum')
    
    status_text = {
        'open': '🟢 Ochiq',
        'waiting_admin': '🟡 Admin kutilmoqda',
        'in_progress': '🔵 Jarayonda',
        'closed': '🔴 Yopiq'
    }.get(ticket['status'], ticket['status'])
    
    priority_text = {
        'low': '🟢 Past',
        'medium': '🟡 O\'rta',
        'high': '🔴 Yuqori'
    }.get(ticket['priority'], ticket['priority'])
    
    # Ticket ma'lumotlari
    text = (
        f"📋 {_('ticket_label').upper()}: {ticket['ticket_number']}\n"
        f"{'='*30}\n\n"
        f"{_('user_label')}: {user_name}\n"
        f"{_('title_label')}: {ticket['title']}\n"
        f"{_('status_label')}: {status_text}\n"
        f"{_('priority_label')}: {priority_text}\n"
        f"{_('created_label')}: {ticket['created_at'][:16]}\n\n"
        f"{_('description_label')}:\n{ticket['description']}\n\n"
        f"{_('messages_label')} ({len(messages)} {_('ticket_count')}):\n"
        f"{'='*30}\n"
    )
    
    # Xabarlarni ko'rsatish
    if messages:
        for i, msg in enumerate(messages[:10], 1):  # Oxirgi 10 ta xabar
            sender = "👤 User" if msg.get('sender_user') else "👨‍💼 Admin"
            content = msg.get('content', 'Media fayl')
            timestamp = msg.get('timestamp', msg.get('created_at', ''))[:16]
            
            text += f"{i}. {sender}\n"
            text += f"   💬 {content[:100]}{'...' if len(content) > 100 else ''}\n"
            text += f"   ⏰ {timestamp}\n\n"
    else:
        text += "Hozircha xabarlar yo'q.\n\n"
    
    text += "Quyidagi tugmalardan birini tanlang:"
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_ticket_admin_actions_keyboard(ticket_id)
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data.startswith("admin_reply_"))
async def admin_reply_ticket(callback: CallbackQuery, state: FSMContext, admin: dict):
    """Ticketga javob berish (soddalashtirilgan)"""
    ticket_id = int(callback.data.split("_")[2])
    
    # Ticket ma'lumotlarini olish
    ticket = await api_client.get_ticket(ticket_id)
    if not ticket:
        await callback.answer(_("ticket_not_found"))
        return
    
    # Faqat o'z ticketiga javob beradi
    if ticket.get('assigned_admin') != admin['id']:
        await callback.answer(_("ticket_not_assigned"))
        return
    
    await state.update_data(replying_ticket_id=ticket_id)
    await state.set_state(AdminStates.replying)
    
    # Media xabar bo'lsa, edit_text ishlamaydi, yangi xabar yuborish kerak
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data=f"admin_ticket_{ticket_id}"
            )
        ]
    ])
    
    try:
        # Avval edit_text ni urinib ko'ramiz
        await callback.message.edit_text(
            _("admin_reply_prompt"),
            reply_markup=cancel_keyboard
        )
    except Exception:
        # Agar xatolik bo'lsa (media xabar), yangi xabar yuboramiz
        await callback.message.answer(
            _("admin_reply_prompt"),
            reply_markup=cancel_keyboard
        )
    
    await callback.answer()


@router.message(StateFilter(AdminStates.replying), F.text.in_(["❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]))
async def cancel_admin_reply(message: Message, state: FSMContext, admin: dict, bot):
    """Javobni bekor qilish"""
    await state.clear()
    # Keyingi savolga o'tish
    await show_next_ticket(message, admin, bot)


@router.message(StateFilter(AdminStates.replying))
async def admin_reply_received(message: Message, state: FSMContext, admin: dict, bot):
    """Admin javobi qabul qilindi va userga yuboriladi"""
    data = await state.get_data()
    ticket_id = data.get('replying_ticket_id')
    
    if not ticket_id:
        await message.answer(_("error_occurred"))
        await state.clear()
        return
    
    # Ticket ma'lumotlarini olish
    ticket = await api_client.get_ticket(ticket_id)
    if not ticket:
        await message.answer(_("ticket_not_found"))
        await state.clear()
        return
    
    # User ma'lumotlarini olish
    user_response = await api_client._make_request('GET', f"user/users/{ticket['user']}/")
    if not user_response:
        await message.answer(_("user_not_found"))
        await state.clear()
        return
    
    user_telegram_id = user_response.get('telegram_id')
    
    # Javob turini aniqlash (file_id bilan)
    content = ""
    content_type = "text"
    file_id = None
    
    if message.text:
        content = message.text
        content_type = "text"
    elif message.photo:
        # Eng katta rasmni olish
        file_id = message.photo[-1].file_id
        content = message.caption or _("admin_sent_image")
        content_type = "image"
    elif message.video:
        file_id = message.video.file_id
        content = message.caption or _("admin_sent_video")
        content_type = "video"
    elif message.audio:
        file_id = message.audio.file_id
        fallback_title = _("unknown")
        content = message.caption or f"{_('admin_sent_audio')}: {message.audio.title or fallback_title}"
        content_type = "audio"
    elif message.voice:
        file_id = message.voice.file_id
        content = _("admin_sent_voice")
        content_type = "audio"
    elif message.document:
        file_id = message.document.file_id
        content = message.caption or f"{_('admin_sent_file')}: {message.document.file_name}"
        content_type = "file"
    elif message.location:
        # Location xabarni qo'llab-quvvatlash
        content = f"📍 {_('location_label')}:\nLatitude: {message.location.latitude}\nLongitude: {message.location.longitude}"
        content_type = "location"
        file_id = None
    else:
        await message.answer(_("unsupported_message_type"))
        return
    
    # Xabarni saqlash (file_id bilan)
    message_created = await api_client.create_message(
        ticket_id=ticket_id,
        sender_admin_id=admin['id'],
        content_type=content_type,
        content=content,
        file_id=file_id
    )
    
    if not message_created:
        await message.answer(_("error_occurred_try_again"))
        await state.clear()
        return
    
    # Ticket statusini yangilash
    await api_client.update_ticket_status(ticket_id, 'in_progress')
    
    # Userga real-time javob yuborish
    try:
        user_lang = user_response.get('language', 'uz')
        with i18n.use_locale(user_lang):
            user_message = (
                f"💬 {_('admin_reply_notification_header')}\n\n"
                f"📋 {_('ticket_label')}: {ticket['ticket_number']}\n"
                f"📝 {_('subject_label')}: {ticket['title']}\n\n"
                f"👨‍💼 {_('admin_reply_label')}:\n{content}"
            )
        
        # Agar media bo'lsa, asl media-ni yuborish (file_id dan foydalanib)
        if file_id and content_type == "image":
            await bot.send_photo(
                chat_id=user_telegram_id,
                photo=file_id,
                caption=user_message
            )
        elif file_id and content_type == "video":
            await bot.send_video(
                chat_id=user_telegram_id,
                video=file_id,
                caption=user_message
            )
        elif file_id and content_type == "audio":
            if message.voice:
                await bot.send_voice(
                    chat_id=user_telegram_id,
                    voice=file_id,
                    caption=user_message
                )
            else:
                await bot.send_audio(
                    chat_id=user_telegram_id,
                    audio=file_id,
                    caption=user_message
                )
        elif file_id and content_type == "file":
            await bot.send_document(
                chat_id=user_telegram_id,
                document=file_id,
                caption=user_message
            )
        elif content_type == "location" and message.location:
            # Location xabarni yuborish
            await bot.send_location(
                chat_id=user_telegram_id,
                latitude=message.location.latitude,
                longitude=message.location.longitude
            )
            # Location ma'lumotlari bilan text yuborish
            await bot.send_message(
                chat_id=user_telegram_id,
                text=user_message
            )
        else:
            # Faqat text
            await bot.send_message(
                chat_id=user_telegram_id,
                text=user_message
            )
        
        logger.info(f"Javob user {user_telegram_id} ga yuborildi")
        
    except Exception as e:
        logger.error(f"Userga javob yuborishda xatolik: {e}")
    
    await state.clear()
    
    # Javob yuborildi xabari ko'rsatish
    confirmation_msg = await message.answer(
        f"✅ Javob yuborildi!\n"
        f"📋 {_('ticket_label')}: {ticket['ticket_number']}"
    )
    
    # Kichik kechikish (xabar ko'rinishi uchun)
    import asyncio
    await asyncio.sleep(1.5)
    
    # Xabarni o'chirish
    try:
        await confirmation_msg.delete()
    except Exception:
        pass
    
    # Javob berilgan savol va javob ko'rsatish (savol va javob ko'rinib qolishi uchun)
    # User ma'lumotlarini olish
    user_response = await api_client._make_request('GET', f"user/users/{ticket['user']}/")
    user_name = _("unknown")
    if user_response:
        user_name = f"{user_response.get('first_name', '')} {user_response.get('last_name', '')}".strip() or user_response.get('username', _("unknown"))
    
    # Ticket xabarlarini olish
    all_messages = await api_client.get_ticket_messages(ticket_id)
    
    # Savol va javob ko'rsatish
    conversation_text = (
        f"📋 {_('ticket_label')}: {ticket['ticket_number']}\n"
        f"{'='*30}\n\n"
        f"👤 {user_name}\n"
        f"📝 {ticket['title']}\n\n"
    )
    
    # Xabarlarni ko'rsatish
    if all_messages:
        for msg in all_messages:
            if msg.get('sender_user'):
                conversation_text += f"👤 User: {msg.get('content', 'Media')}\n\n"
            elif msg.get('sender_admin'):
                conversation_text += f"👨‍💼 Admin: {msg.get('content', 'Media')}\n\n"
    
    await message.answer(conversation_text)
    
    # Keyingi kutayotgan savolni ko'rsatish (agar bor bo'lsa)
    tickets = await api_client.get_admin_tickets(admin['id'])
    if tickets:
        waiting_tickets = [
            t for t in tickets 
            if t['status'] in ['waiting_admin', 'in_progress', 'open']
            and t['id'] != ticket_id
        ]
        
        # Admin javob bermagan savollarni filtrlash
        unanswered_tickets = []
        for ticket_data in waiting_tickets:
            # Ticket xabarlarini olish
            messages = await api_client.get_ticket_messages(ticket_data['id'])
            
            # Admin javobi borligini tekshirish
            has_admin_reply = False
            if messages:
                # Agar xabarlar ichida admin javobi bo'lsa
                for msg in messages:
                    if msg.get('sender_admin') is not None and msg.get('sender_admin') != '':
                        has_admin_reply = True
                        break
            
            # Agar admin javob bermagan bo'lsa, ro'yxatga qo'shish
            if not has_admin_reply:
                unanswered_tickets.append(ticket_data)
        
        if unanswered_tickets:
            # Keyingi savolni ko'rsatish (oddiy format)
            next_ticket_data = min(unanswered_tickets, key=lambda x: x.get('created_at', ''))
            next_ticket = await api_client.get_ticket(next_ticket_data['id'])
            
            if next_ticket:
                # User ma'lumotlarini olish
                user_response = await api_client._make_request('GET', f"user/users/{next_ticket['user']}/")
                user_name = _("unknown")
                if user_response:
                    user_name = f"{user_response.get('first_name', '')} {user_response.get('last_name', '')}".strip() or user_response.get('username', _("unknown"))
                
                priority_emoji = {
                    'low': '🟢',
                    'medium': '🟡',
                    'high': '🔴'
                }.get(next_ticket.get('priority', 'medium'), '🟡')
                
                created_time = next_ticket['created_at'][:16].replace('T', ' ')
                
                text = (
                    f"👤 {user_name}\n"
                    f"📝 {next_ticket['title']}\n"
                    f"{priority_emoji} {next_ticket.get('priority', 'medium').title()}\n"
                    f"📅 {created_time}\n"
                    f"📋 {_('ticket_label')}: {next_ticket['ticket_number']}\n\n"
                    f"💬 {next_ticket['description']}"
                )
                
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=_("reply"),
                            callback_data=f"admin_reply_{next_ticket['id']}"
                        ),
                        InlineKeyboardButton(
                            text=_("close"),
                            callback_data=f"admin_close_no_reply_{next_ticket['id']}"
                        )
                    ]
                ])
                
                await message.answer(text, reply_markup=keyboard)
        else:
            # Barcha savollar hal qilindi
            await message.answer(_("admin_all_done"))


@router.callback_query(F.data.startswith("admin_progress_"))
async def set_ticket_in_progress(callback: CallbackQuery, admin: dict):
    """Ticketni jarayonda deb belgilash"""
    ticket_id = int(callback.data.split("_")[2])
    
    # Ticket ma'lumotlarini olish va tekshirish
    ticket = await api_client.get_ticket(ticket_id)
    if not ticket:
        await callback.answer(_("ticket_not_found"))
        return
    
    # Faqat o'z ticketini boshqaradi
    if ticket.get('assigned_admin') != admin['id']:
        await callback.answer(_("ticket_not_assigned"))
        return
    
    result = await api_client.update_ticket_status(ticket_id, 'in_progress')
    
    if result:
        await callback.answer(_("ticket_in_progress"))
    else:
        await callback.answer(_("error_occurred"))


@router.callback_query(F.data.startswith("admin_close_no_reply_"))
async def close_ticket_no_reply(callback: CallbackQuery, admin: dict, bot):
    """Ticketni javobsiz yopish"""
    ticket_id = int(callback.data.split("_")[4])
    
    # Ticket ma'lumotlarini olish va tekshirish
    ticket = await api_client.get_ticket(ticket_id)
    if not ticket:
        await callback.answer(_("ticket_not_found"))
        return
    
    # Faqat o'z ticketini yopadi
    if ticket.get('assigned_admin') != admin['id']:
        await callback.answer(_("ticket_not_assigned"))
        return
    
    # Ticketni yopish
    result = await api_client.close_ticket(
        ticket_id=ticket_id,
        admin_id=admin['id'],
        close_reason="Admin tomonidan javobsiz yopildi"
    )
    
    if result:
        await callback.answer(_("ticket_closed_success"))
        # Keyingi savolga o'tish (xabar ko'rsatmasdan)
        await callback.message.delete()
        await show_next_ticket(callback, admin, bot)
    else:
        await callback.answer(_("error_occurred"))


@router.callback_query(F.data.startswith("admin_close_"))
async def close_ticket_confirm(callback: CallbackQuery, state: FSMContext, admin: dict):
    """Ticketni yopishni tasdiqlash"""
    ticket_id = int(callback.data.split("_")[2])
    
    # Ticket ma'lumotlarini olish va tekshirish
    ticket = await api_client.get_ticket(ticket_id)
    if not ticket:
        await callback.answer(_("ticket_not_found"))
        return
    
    # Faqat o'z ticketini yopadi
    if ticket.get('assigned_admin') != admin['id']:
        await callback.answer(_("ticket_not_assigned"))
        return
    
    await state.update_data(closing_ticket_id=ticket_id)
    await state.set_state(AdminStates.writing_close_reason)
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data=f"admin_ticket_{ticket_id}"
            )
        ]
    ])
    
    try:
        await callback.message.edit_text(
            _("enter_closing_reason"),
            reply_markup=cancel_keyboard
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.message.answer(
        _("enter_closing_reason_prompt"),
        reply_markup=get_admin_cancel_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_next_ticket")
async def next_ticket_handler(callback: CallbackQuery, admin: dict, bot):
    """Keyingi savolga o'tish"""
    await show_next_ticket(callback, admin, bot)


@router.message(StateFilter(AdminStates.writing_close_reason))
async def close_ticket_with_reason(message: Message, state: FSMContext, admin: dict, bot):
    """Ticket yopish"""
    if message.text in [_("cancel"), "❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]:
        await state.clear()
        await show_next_ticket(message, admin, bot)
        return
    
    data = await state.get_data()
    ticket_id = data.get('closing_ticket_id')
    
    close_reason = message.text if message.text else "Admin tomonidan yopildi"
    
    result = await api_client.close_ticket(
        ticket_id=ticket_id,
        admin_id=admin['id'],
        close_reason=close_reason
    )
    
    await state.clear()
    
    # Keyingi savolga o'tish (xabar ko'rsatmasdan)
    if result:
        await show_next_ticket(message, admin, bot)
    else:
        await show_next_ticket(message, admin, bot)


@router.message(F.text.in_(["👤 User rejimi", "👤 Режим пользователя", "👤 User mode"]))
async def switch_to_user_mode(message: Message):
    """User rejimiga o'tish"""
    await message.answer(
        _("admin_user_mode") + "\n\n" + _("admin_menu_text"),
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text.in_(["📊 Statistika", "📊 Статистика", "📊 Statistics"]))
async def admin_statistics(message: Message, admin: dict, db_user: dict):
    """Admin statistikasi"""
    if not admin:
        await message.answer(_("admin_not_found"))
        return
    
    # Avval 10 minutdan o'shgan javobsiz ticketlarni yopib tashlaymiz
    await api_client.close_expired_tickets()
    
    tickets = await api_client.get_admin_tickets(admin['id'])
    
    if not tickets:
        await message.answer(_("admin_no_tickets"))
        return
    
    # Vaqt bo'yicha statistika
    from datetime import date, timedelta
    today = date.today()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    
    # Bugungi, kechagi, haftalik
    today_tickets = [t for t in tickets if t['created_at'].startswith(today.isoformat())]
    yesterday_tickets = [t for t in tickets if t['created_at'].startswith(yesterday.isoformat())]
    week_tickets = [t for t in tickets if t['created_at'] >= week_ago.isoformat()]
    
    # Status bo'yicha
    total = len(tickets)
    open_count = len([t for t in tickets if t['status'] == 'open'])
    waiting_count = len([t for t in tickets if t['status'] == 'waiting_admin'])
    in_progress_count = len([t for t in tickets if t['status'] == 'in_progress'])
    closed_count = len([t for t in tickets if t['status'] == 'closed'])
    
    # Prioritet bo'yicha
    high_priority = len([t for t in tickets if t.get('priority') == 'high'])
    medium_priority = len([t for t in tickets if t.get('priority') == 'medium'])
    low_priority = len([t for t in tickets if t.get('priority') == 'low'])
    
    # Get user language and fetch categories
    user_lang = db_user.get('language', 'uz')
    categories = await api_client.get_categories(lang=user_lang)
    category_stats = {}
    for category in categories:
        cat_tickets = [t for t in tickets if t['category'] == category['id']]
        if cat_tickets:
            category_stats[category['name']] = len(cat_tickets)
    
    stats_text = (
        f"{_('admin_stats_header')}\n"
        f"{'='*25}\n\n"
        f"{_('stats_time_based')}:\n"
        f"{_('stats_today')}: {len(today_tickets)} {_('ticket_count')}\n"
        f"{_('stats_yesterday')}: {len(yesterday_tickets)} {_('ticket_count')}\n"
        f"{_('stats_this_week')}: {len(week_tickets)} {_('ticket_count')}\n\n"
        f"{_('stats_by_status')}:\n"
        f"{_('stats_total_tickets')}: {total} {_('ticket_count')}\n"
        f"{_('stats_open')}: {open_count}\n"
        f"{_('stats_waiting')}: {waiting_count}\n"
        f"{_('stats_in_progress')}: {in_progress_count}\n"
        f"{_('stats_closed')}: {closed_count}\n\n"
        f"{_('stats_priority_header')}:\n"
        f"{_('ticket_priority_high')}: {high_priority}\n"
        f"{_('ticket_priority_medium')}: {medium_priority}\n"
        f"{_('ticket_priority_low')}: {low_priority}\n\n"
    )
    
    if category_stats:
        stats_text += f"{_('category_label_header')}\n"
        for cat_name, count in category_stats.items():
            stats_text += f"• {cat_name}: {count} {_('ticket_count')}\n"
        stats_text += "\n"
    
    # Samaradorlik
    if total > 0:
        efficiency = (closed_count / total) * 100
        stats_text += f"{_('efficiency')}: {efficiency:.1f}%\n"
        
        # Bugungi samaradorlik
        if today_tickets:
            today_closed = len([t for t in today_tickets if t['status'] == 'closed'])
            today_efficiency = (today_closed / len(today_tickets)) * 100
            stats_text += f"{_('stats_today_efficiency')}: {today_efficiency:.1f}%"
    
    # "Orqaga qaytish" tugmasi bilan
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    stats_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_("back_to_menu"),
                callback_data="admin_menu"
            )
        ]
    ])
    
    await message.answer(stats_text, reply_markup=stats_keyboard)


@router.callback_query(F.data == "admin_tickets")
async def back_to_admin_tickets(callback: CallbackQuery, admin: dict):
    """Admin ticketlariga qaytish (sukut bo'yicha bugun)"""
    if not admin:
        await callback.answer(_("admin_not_found"))
        return
    
    tickets = await api_client.get_admin_tickets(admin['id'], date_filter='today')
    
    try:
        await callback.message.edit_text(
            _("admin_my_tickets_count").format(count=len(tickets)),
            reply_markup=get_admin_tickets_keyboard(tickets, current_filter='today')
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    
    await callback.answer()


@router.callback_query(F.data.startswith("admin_filter_"))
async def admin_filter_tickets(callback: CallbackQuery, admin: dict):
    """Filtrni o'zgartirish"""
    date_filter = callback.data.split("_")[2]
    
    tickets = await api_client.get_admin_tickets(admin['id'], date_filter=date_filter)
    
    try:
        await callback.message.edit_text(
            _("admin_my_tickets_count").format(count=len(tickets)),
            reply_markup=get_admin_tickets_keyboard(tickets, current_filter=date_filter)
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    
    await callback.answer()


@router.callback_query(F.data == "admin_pick_date")
async def admin_pick_date(callback: CallbackQuery, state: FSMContext):
    """Sana kiritishni so'rash"""
    await state.set_state(AdminStates.picking_date)
    await callback.message.answer(
        _("admin_pick_date_prompt"),
        reply_markup=get_admin_cancel_keyboard()
    )
    await callback.answer()


@router.message(AdminStates.picking_date, F.text)
async def admin_date_picked(message: Message, state: FSMContext, admin: dict):
    """Kiritilgan sanani qayta ishlash"""
    date_text = message.text.strip()
    
    # Bekor qilish
    if any(keyword in date_text for keyword in ["Bekor", "Отмена", "Cancel"]):
        await state.clear()
        # Qayta mening ticketlarimga
        tickets = await api_client.get_admin_tickets(admin['id'], date_filter='today')
        await message.answer(
            _("admin_my_tickets_count").format(count=len(tickets)),
            reply_markup=get_admin_tickets_keyboard(tickets, current_filter='today')
        )
        return

    # Sanani formatlashga urinish
    target_date = None
    formats = ['%d.%m.%Y', '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y']
    
    # Yil qo'shish (agar faqat DD.MM bo'lsa)
    if len(date_text.split('.')) == 2:
        date_text += f".{datetime.now().year}"

    for fmt in formats:
        try:
            target_date = datetime.strptime(date_text, fmt).date()
            break
        except ValueError:
            continue
            
    if not target_date:
        await message.answer(_("admin_invalid_date_format"))
        return
        
    await state.clear()
    date_str = target_date.strftime('%Y-%m-%d')
    tickets = await api_client.get_admin_tickets(admin['id'], date_filter=date_str)
    await message.answer(
        _("admin_my_tickets_count").format(count=len(tickets)),
        reply_markup=get_admin_tickets_keyboard(tickets, current_filter=date_str)
    )


@router.callback_query(F.data.startswith("refresh_admin_tickets"))
async def refresh_admin_tickets(callback: CallbackQuery, admin: dict):
    """Admin ticketlarini yangilash (filtrni saqlagan holda)"""
    if not admin:
        await callback.answer(_("admin_not_found"))
        return
    
    # Filtrni aniqlash
    parts = callback.data.split("_")
    date_filter = parts[3] if len(parts) > 3 else 'today'
    
    tickets = await api_client.get_admin_tickets(admin['id'], date_filter=date_filter)
    
    try:
        await callback.message.edit_text(
            _("admin_my_tickets_count").format(count=len(tickets)),
            reply_markup=get_admin_tickets_keyboard(tickets, current_filter=date_filter)
        )
        await callback.answer(_("updated_success"))
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            await callback.answer(_("updated_success"))
        else:
            raise


@router.callback_query(F.data == "admin_menu")
async def back_to_admin_menu(callback: CallbackQuery, state: FSMContext):
    """Admin menyusiga qaytish"""
    await state.clear()
    try:
        await callback.message.edit_text(
            _("admin_menu_title"),
            reply_markup=None
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    except Exception:
        pass
    
    await callback.message.answer(
        _("admin_menu_text"),
        reply_markup=get_admin_main_menu_keyboard()
    )
    await callback.answer()
