# flake8: noqa
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fsm.states import UserStates
from keyboards.user import (
    get_main_menu_keyboard, get_categories_keyboard, 
    get_my_tickets_keyboard, get_ticket_actions_keyboard,
    get_priority_keyboard, get_cancel_keyboard, get_settings_keyboard
)
from keyboards.language import get_language_keyboard
from aiogram.utils.i18n import gettext as _
from datetime import datetime, timezone as dt_timezone
from services.api import api_client

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, db_user: dict, user_role: str, is_super_admin: bool, admin: dict, user_language: str = 'uz'):
    """Start komandasi"""
    # Agar til tanlanmagan bo'lsa, til tanlashni ko'rsatish
    if not user_language or user_language not in ['uz', 'ru', 'en']:
        await message.answer(
            _("select_language"),
            reply_markup=get_language_keyboard()
        )
        return
    
    user_name = message.from_user.first_name or "User"
    
    # Role ga qarab xush kelibsiz xabari
    if is_super_admin:
        from keyboards.admin import get_super_admin_menu_keyboard
        await message.answer(
            _("welcome_super_admin").format(name=user_name),
            reply_markup=get_super_admin_menu_keyboard()
        )
    elif admin and not admin.get('is_blocked'):
        # Admin uchun alohida panel
        from keyboards.admin import get_admin_main_menu_keyboard
        await message.answer(
            _("welcome_admin").format(name=user_name),
            reply_markup=get_admin_main_menu_keyboard()
        )
    else:
        # Oddiy user
        await message.answer(
            _("welcome_user").format(name=user_name),
            reply_markup=get_main_menu_keyboard()
        )


@router.message(F.text.in_(["⚙️ Sozlamalar", "⚙️ Settings", "⚙️ Настройки"]))
async def settings_menu(message: Message):
    """Sozlamalar menyusi"""
    await message.answer(
        _("settings_message"),
        reply_markup=get_settings_keyboard()
    )


@router.message(F.text.contains("Language") | F.text.contains("Til") | F.text.contains("Язык"))
async def select_language_from_settings(message: Message):
    """Til tanlash (sozlamalardan) - Keng match"""
    # Debug logging
    logger.info(f"Language button pressed. Received text: '{message.text}'")
    
    # Faqat language button bo'lsa
    if any(keyword in message.text for keyword in ["Language", "Til", "Язык"]):
        await message.answer(
            _("select_language"),
            reply_markup=get_language_keyboard()
        )


@router.message(F.text.in_(["🔙 Bosh menyu", "🔙 Main menu", "🔙 Главное меню"]))
async def back_to_main_menu_handler(message: Message, user_role: str, is_super_admin: bool, admin: dict):
    """Bosh menyuga qaytish"""
    user_name = message.from_user.first_name or "User"
    
    if is_super_admin:
        from keyboards.admin import get_super_admin_menu_keyboard
        await message.answer(
            _("welcome_super_admin").format(name=user_name),
            reply_markup=get_super_admin_menu_keyboard()
        )
    elif admin and not admin.get('is_blocked'):
        from keyboards.admin import get_admin_main_menu_keyboard
        await message.answer(
            _("welcome_admin").format(name=user_name),
            reply_markup=get_admin_main_menu_keyboard()
        )
    else:
        await message.answer(
            _("welcome_user").format(name=user_name),
            reply_markup=get_main_menu_keyboard()
        )




@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, db_user: dict, user_role: str, is_super_admin: bool, admin: dict, **kwargs):
    """Til o'rnatish"""
    from middlewares.i18n import i18n
    from aiogram.fsm.context import FSMContext
    
    lang_code = callback.data.split("_")[1]  # uz, ru, en
    
    if not db_user or not db_user.get('id'):
        await callback.answer(_("error_occurred"))
        return
    
    # Language'ni API orqali yangilash
    result = await api_client._make_request(
        'PATCH',
        f"user/users/{db_user['id']}/",
        data={'language': lang_code}
    )
    
    if result:
        # CRITICAL: db_user ni yangilash (bu kerakda middleware uchun)
        db_user['language'] = lang_code
        
        # Locale ni FORCE yangilash
        i18n.ctx_locale.set(lang_code)
        
        # Til nomi
        lang_names = {
            'uz': "O'zbek",
            'ru': 'Русский',
            'en': 'English'
        }
        lang_name = lang_names.get(lang_code, lang_code)
        
        # Yangi locale context'da barcha xabarlar
        with i18n.use_locale(lang_code):
            await callback.answer(_("language_set").format(lang=lang_name))
            
            # Xabarni o'chirish
            try:
                await callback.message.delete()
            except Exception:
                pass
            
            # Yangi tilda xush kelibsiz xabari va menyu
            user_name = callback.from_user.first_name or "User"
            from keyboards.admin import get_super_admin_menu_keyboard, get_admin_main_menu_keyboard
            
            if is_super_admin:
                await callback.message.answer(
                    _("welcome_super_admin").format(name=user_name),
                    reply_markup=get_super_admin_menu_keyboard()
                )
            elif admin and not admin.get('is_blocked'):
                await callback.message.answer(
                    _("welcome_admin").format(name=user_name),
                    reply_markup=get_admin_main_menu_keyboard()
                )
            else:
                await callback.message.answer(
                    _("welcome_user").format(name=user_name),
                    reply_markup=get_main_menu_keyboard()
                )
    else:
        await callback.answer(_("error_occurred"))


@router.message(F.text.in_(["📝 Yangi savol", "📝 New question", "📝 Новый вопрос"]))
async def new_question(message: Message, state: FSMContext, db_user: dict, user_role: str, admin: dict, user_language: str = 'uz'):
    """Yangi savol yaratish (vaqt cheklovi bilan)"""
    # Admin va Super Admin uchun bu funksiya ishlamaydi
    if user_role in ['admin', 'super_admin']:
        from keyboards.admin import get_admin_main_menu_keyboard
        await message.answer(
            _("admin_mode_only"),
            reply_markup=get_admin_main_menu_keyboard() if admin else None
        )
        return

    if not db_user or not db_user.get('id'):
        await message.answer(_("error_restart"))
        return
    
    # Foydalanuvchining ochiq ticketi borligini tekshirish
    from datetime import datetime, timedelta
    
    tickets = await api_client.get_user_tickets(db_user['id'])
    
    if tickets:
        open_tickets = [t for t in tickets if t['status'] != 'closed']
        
        if open_tickets:
            # Eng so'nggi ochiq ticket
            last_ticket = max(open_tickets, key=lambda x: x.get('created_at', ''))
            last_time_str = last_ticket.get('created_at', '')
            
            if last_time_str:
                try:
                    last_time = datetime.fromisoformat(last_time_str.replace('Z', '+00:00'))
                    # Ensure last_time is aware UTC
                    if last_time.tzinfo is None:
                        last_time = last_time.replace(tzinfo=dt_timezone.utc)
                    
                    # Ticket xabarlarini olish
                    ticket_messages = await api_client.get_ticket_messages(last_ticket['id'])
                    
                    # Admin javobi borligini tekshirish (oddiy va ishonchli usul)
                    has_admin_reply = False
                    if ticket_messages:
                        # Agar xabarlar ichida admin javobi bo'lsa (sender_admin None emas va bo'sh emas)
                        for msg in ticket_messages:
                            sender_admin = msg.get('sender_admin')
                            if sender_admin is not None and sender_admin != '' and sender_admin != 0:
                                has_admin_reply = True
                                break
                    
                    logger.info(
                        f"Ticket {last_ticket['id']} - "
                        f"Admin javob: {has_admin_reply}, "
                        f"Xabarlar: {len(ticket_messages) if ticket_messages else 0}, "
                        f"Status: {last_ticket.get('status')}"
                    )
                    
                    # Agar admin javob bersa, yangi savol yubora oladi
                    if has_admin_reply:
                        # Javob keldi, yangi savol yubora oladi
                        logger.info(f"User {db_user['id']} - Admin javob bor, yangi savol yubora oladi")
                        # Davom etadi, kategoriya tanlashga o'tadi (return qilmaydi)
                    else:
                        # Javob kelmagan, 10 minut kutish kerak
                        time_diff = datetime.now(dt_timezone.utc) - last_time
                        minutes_passed = time_diff.total_seconds() / 60
                        
                        if minutes_passed < 10:
                            remaining_minutes = 10 - int(minutes_passed)
                            remaining_seconds = int((10 - minutes_passed) * 60) % 60

                            await message.answer(
                                _("user_has_open_ticket").format(
                                    ticket_number=last_ticket.get('ticket_number', 'N/A'),
                                    title=last_ticket.get('title', 'N/A'),
                                    status=last_ticket.get('status', 'N/A'),
                                    minutes=remaining_minutes
                                ),
                                reply_markup=get_main_menu_keyboard()
                            )
                            return
                        else:
                            # 10 minut o'tgan, lekin javob kelmagan - yangi savol yubora oladi
                            # Avval eski ticketni yopamiz
                            await api_client.close_expired_tickets()
                            
                            await message.answer(
                                _("ticket_time_expired").format(
                                    ticket_number=last_ticket.get('ticket_number', 'N/A')
                                ),
                                reply_markup=get_main_menu_keyboard()
                            )
                            # Yangi savol yubora olish uchun davom etish
                except Exception as e:
                    logger.error(f"Vaqt tekshirishda xatolik: {e}")
                    # Xatolik bo'lsa ham davom etish
    
    # Agar vaqt cheklovi yo'q bo'lsa, kategoriya tanlash
    
    # Get user language and fetch categories
    user_lang = db_user.get('language', 'uz')
    categories = await api_client.get_categories(lang=user_lang)
    if not categories:
        await message.answer(
            _("no_categories_available"),
            reply_markup=get_main_menu_keyboard()
        )
        return

    # Kategoriyalar haqida ma'lumot
    category_info = _("available_categories_header") + "\n\n"
    for i, cat in enumerate(categories, 1):
        category_info += f"{i}. {cat['name']}\n"
        if cat.get('description'):
            category_info += f"   💬 {cat['description']}\n"
        category_info += "\n"

    await message.answer(
        f"{category_info}{_('select_category_prompt')}",
        reply_markup=get_categories_keyboard(categories)
    )
    await state.set_state(UserStates.choosing_category)


@router.callback_query(F.data.startswith("category_"), StateFilter(UserStates.choosing_category))
async def category_selected(callback: CallbackQuery, state: FSMContext):
    """Kategoriya tanlandi"""
    category_id = int(callback.data.split("_")[1])

    # Kategoriya ma'lumotlarini olish
    category = await api_client.get_category(category_id)
    if not category:
        await callback.answer(_("category_not_found"))
        return

    await state.update_data(selected_category=category)

    try:
        await callback.message.edit_text(
            _("category_selected_header").format(category_name=category['name']),
            reply_markup=None
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.message.answer(
        _("write_question_prompt"),
        reply_markup=get_cancel_keyboard()
    )

    await state.set_state(UserStates.writing_message)
    await callback.answer()


@router.message(StateFilter(UserStates.writing_message), F.text.in_(["❌ Bekor qilish", "❌ Cancel", "❌ Отменить"]))
async def cancel_question(message: Message, state: FSMContext):
    """Savolni bekor qilish"""
    await state.clear()
    await message.answer(
        _("question_cancelled"),
        reply_markup=get_main_menu_keyboard()
    )


@router.message(StateFilter(UserStates.writing_message))
async def question_received(message: Message, state: FSMContext, db_user: dict):
    """Savol qabul qilindi"""
    data = await state.get_data()
    category = data.get('selected_category')

    if not category:
        await message.answer(_("error_occurred_restart"))
        await state.clear()
        return
    
    # Ticket yaratish
    content = ""
    content_type = "text"
    file_id = None
    
    if message.text:
        content = message.text
        content_type = "text"
    elif message.photo:
        # Eng katta rasmni olish
        file_id = message.photo[-1].file_id
        content = message.caption or _("image_sent")
        content_type = "image"
    elif message.video:
        file_id = message.video.file_id
        content = message.caption or _("video_sent")
        content_type = "video"
    elif message.audio:
        file_id = message.audio.file_id
        content = message.caption or _("audio_sent").format(title=message.audio.title or _("unknown"))
        content_type = "audio"
    elif message.voice:
        file_id = message.voice.file_id
        content = _("voice_message")
        content_type = "audio"
    elif message.document:
        file_id = message.document.file_id
        content = message.caption or _("file_sent").format(filename=message.document.file_name)
        content_type = "file"
    elif message.location:
        # Location xabarni to'liq qo'llab-quvvatlash
        content = _("location_sent").format(
            latitude=message.location.latitude,
            longitude=message.location.longitude
        )
        content_type = "location"
        # Location uchun file_id yo'q, lekin ma'lumotlarni saqlaymiz
        file_id = None
    else:
        await message.answer(_("message_type_not_supported"))
        return
    
    # Ticket yaratish (description uchun text ishlatiladi)
    ticket_description = content
    if not ticket_description:
        ticket_description = f"{content_type.title()} yuborildi"
    
    ticket = await api_client.create_ticket(
        user_id=db_user['id'],
        title=ticket_description[:50] + "..." if len(ticket_description) > 50 else ticket_description,
        category_id=category['id'],
        description=ticket_description,
        priority='medium'
    )

    if not ticket:
        await message.answer(_("error_try_again"))
        return
    
    # Birinchi xabarni yaratish (file_id bilan)
    await api_client.create_message(
        ticket_id=ticket['id'],
        sender_user_id=db_user['id'],
        content_type=content_type,
        content=content,
        file_id=file_id
    )
    
    # Assigned admin-ga real-time notification yuborish
    assigned_admin_id = ticket.get('assigned_admin')
    if assigned_admin_id:
        try:
            # Admin ma'lumotlarini olish
            admin_response = await api_client._make_request('GET', f"admin/admins/{assigned_admin_id}/")
            if admin_response:
                admin_user_response = await api_client._make_request('GET', f"user/users/{admin_response['user']}/")
                if admin_user_response:
                    admin_telegram_id = admin_user_response.get('telegram_id')
                    
                    # Bot instance-ni olish
                    from aiogram import Bot
                    from config import BOT_TOKEN
                    notification_bot = Bot(token=BOT_TOKEN)
                    
                    # Admin-ga savol ko'rsatish (media bilan)
                    priority_emoji = {
                        'low': '🟢',
                        'medium': '🟡',
                        'high': '🔴'
                    }.get(ticket.get('priority', 'medium'), '🟡')

                    created_time = ticket['created_at'][:16].replace('T', ' ')
                    user_name = message.from_user.first_name or _("unknown")

                    notification_text = (
                        f"👤 {user_name}\n"
                        f"📝 {ticket['title']}\n"
                        f"{priority_emoji} {ticket.get('priority', 'medium').title()}\n"
                        f"📅 {created_time}\n"
                        f"📋 {ticket['ticket_number']}\n\n"
                        f"💬 {ticket['description']}"
                    )
                    
                    # Inline tugmalar
                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=_("reply_button"),
                                callback_data=f"admin_reply_{ticket['id']}"
                            ),
                            InlineKeyboardButton(
                                text=_("close_button"),
                                callback_data=f"admin_close_no_reply_{ticket['id']}"
                            )
                        ]
                    ])
                    
                    # Media bilan yuborish
                    try:
                        if content_type == "image" and file_id:
                            await notification_bot.send_photo(
                                chat_id=admin_telegram_id,
                                photo=file_id,
                                caption=notification_text,
                                reply_markup=keyboard
                            )
                        elif content_type == "video" and file_id:
                            await notification_bot.send_video(
                                chat_id=admin_telegram_id,
                                video=file_id,
                                caption=notification_text,
                                reply_markup=keyboard
                            )
                        elif content_type == "audio" and file_id:
                            if message.voice:
                                await notification_bot.send_voice(
                                    chat_id=admin_telegram_id,
                                    voice=file_id,
                                    caption=notification_text,
                                    reply_markup=keyboard
                                )
                            else:
                                await notification_bot.send_audio(
                                    chat_id=admin_telegram_id,
                                    audio=file_id,
                                    caption=notification_text,
                                    reply_markup=keyboard
                                )
                        elif content_type == "file" and file_id:
                            await notification_bot.send_document(
                                chat_id=admin_telegram_id,
                                document=file_id,
                                caption=notification_text,
                                reply_markup=keyboard
                            )
                        elif content_type == "location" and message.location:
                            # Location xabarni yuborish
                            await notification_bot.send_location(
                                chat_id=admin_telegram_id,
                                latitude=message.location.latitude,
                                longitude=message.location.longitude
                            )
                            # Location ma'lumotlari bilan text yuborish
                            await notification_bot.send_message(
                                chat_id=admin_telegram_id,
                                text=notification_text,
                                reply_markup=keyboard
                            )
                        else:
                            # Faqat text
                            await notification_bot.send_message(
                                chat_id=admin_telegram_id,
                                text=notification_text,
                                reply_markup=keyboard
                            )
                    except Exception as e:
                        logger.error(f"Admin-ga media yuborishda xatolik: {e}")
                        # Xatolik bo'lsa, faqat text yuborish
                        await notification_bot.send_message(
                            chat_id=admin_telegram_id,
                            text=notification_text,
                            reply_markup=keyboard
                        )
                    
                    await notification_bot.session.close()
                    
                    logger.info(f"Notification admin {admin_telegram_id} ga yuborildi")
        except Exception as e:
            logger.error(f"Admin-ga notification yuborishda xatolik: {e}")
    
    await state.clear()
    await message.answer(
        _("question_accepted").format(
            ticket_number=ticket['ticket_number'],
            category=category['name']
        ),
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text.in_(["📋 Mening savollarim", "📋 My questions", "📋 Мои вопросы"]))
async def my_questions(message: Message, db_user: dict, user_role: str, admin: dict):
    """Foydalanuvchi savollarini ko'rsatish"""
    # Admin va Super Admin uchun bu funksiya ishlamaydi
    if user_role in ['admin', 'super_admin']:
        from keyboards.admin import get_admin_main_menu_keyboard
        await message.answer(
            _("admin_mode_only"),
            reply_markup=get_admin_main_menu_keyboard() if admin else None
        )
        return

    if not db_user or not db_user.get('id'):
        await message.answer(_("error_restart"))
        return

    tickets = await api_client.get_user_tickets(db_user['id'])

    if not tickets:
        await message.answer(
            _("no_questions_yet"),
            reply_markup=get_main_menu_keyboard()
        )
        return

    await message.answer(
        _("your_questions"),
        reply_markup=get_my_tickets_keyboard(tickets)
    )


@router.callback_query(F.data.startswith("ticket_"))
async def show_ticket_details(callback: CallbackQuery):
    """Ticket tafsilotlarini ko'rsatish"""
    ticket_id = int(callback.data.split("_")[1])

    ticket = await api_client.get_ticket(ticket_id)
    if not ticket:
        await callback.answer(_("ticket_not_found"))
        return

    status_text = {
        'open': _("ticket_status_open"),
        'waiting_admin': _("ticket_status_waiting_admin"),
        'in_progress': _("ticket_status_in_progress"),
        'closed': _("ticket_status_closed")
    }.get(ticket['status'], ticket['status'])

    priority_text = {
        'low': _("priority_low"),
        'medium': _("priority_medium"),
        'high': _("priority_high")
    }.get(ticket['priority'], ticket['priority'])

    text = (
        f"📋 {_('ticket_label')}: {ticket['ticket_number']}\n"
        f"📝 {_('title_label')}: {ticket['title']}\n"
        f"📊 {_('status_label')}: {status_text}\n"
        f"⚡ {_('priority_label')}: {priority_text}\n"
        f"📅 {_('created_label')}: {ticket['created_at'][:10]}\n\n"
        f"📄 {_('description_label')}:\n{ticket['description']}"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=get_ticket_actions_keyboard(ticket_id)
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.message(F.text.in_(["ℹ️ Yordam", "ℹ️ Help", "ℹ️ Помощь"]))
async def help_command(message: Message, user_role: str, admin: dict):
    """Yordam"""
    # Admin va Super Admin uchun bu funksiya ishlamaydi
    if user_role in ['admin', 'super_admin']:
        from keyboards.admin import get_admin_main_menu_keyboard
        await message.answer(
            _("admin_mode_only"),
            reply_markup=get_admin_main_menu_keyboard() if admin else None
        )
        return

    await message.answer(_("help_text"), reply_markup=get_main_menu_keyboard())


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    """Bosh menyuga qaytish"""
    await state.clear()
    try:
        await callback.message.edit_text(
            _("main_menu_header"),
            reply_markup=None
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.message.answer(
        _("select_button_prompt"),
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()
