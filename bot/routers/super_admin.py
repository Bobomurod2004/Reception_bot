from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fsm.states import SuperAdminStates
from keyboards.admin import (
    get_super_admin_menu_keyboard, get_admins_management_keyboard,
    get_categories_management_keyboard, get_admin_cancel_keyboard
)
from keyboards.user import get_main_menu_keyboard, get_settings_keyboard
from keyboards.admin import get_admin_main_menu_keyboard
from keyboards.language import get_language_keyboard
from aiogram.utils.i18n import gettext as _
from middlewares.i18n import i18n
from services.api import api_client

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text.in_(["⚙️ Sozlamalar", "⚙️ Settings", "⚙️ Настройки"]))
async def super_admin_settings_menu(message: Message):
    """Super admin sozlamalar menyusi"""
    await message.answer(
        _("settings_message"),
        reply_markup=get_settings_keyboard()
    )


@router.message(F.text.contains("Language") | F.text.contains("Til") | F.text.contains("Язык"))
async def super_admin_select_language(message: Message):
    """Super admin til tanlash - Keng match"""
    logger.info(f"Super admin language button pressed. Received text: '{message.text}'")
    
    if any(keyword in message.text for keyword in ["Language", "Til", "Язык"]):
        await message.answer(
            _("select_language"),
            reply_markup=get_language_keyboard()
        )


@router.message(Command("superadmin"))
async def cmd_super_admin(message: Message, is_super_admin: bool):
    """Super admin rejimi"""
    if not is_super_admin:
        await message.answer("Sizda super admin huquqlari yo'q.")
        return
    
    # Umumiy statistika
    all_tickets = await api_client._make_request('GET', 'ticket/tickets/')
    total_tickets = len(all_tickets.get('results', [])) if all_tickets else 0
    
    # Bugungi ticketlar
    from datetime import date
    today = date.today().isoformat()
    today_tickets = 0
    if all_tickets and all_tickets.get('results'):
        today_tickets = len([t for t in all_tickets['results'] if t['created_at'].startswith(today)])
    
    await message.answer(
        f"👑 Super Admin Panel\n\n"
        f"📊 Tizim holati:\n"
        f"• Jami ticketlar: {total_tickets}\n"
        f"• Bugungi ticketlar: {today_tickets}\n\n"
        f"Boshqaruv funksiyalari:",
        reply_markup=get_super_admin_menu_keyboard()
    )


@router.message(F.text.in_(["👥 Adminlar", "👥 Администраторы", "👥 Admins"]))
async def manage_admins(message: Message, is_super_admin: bool):
    """Adminlarni boshqarish"""
    if not is_super_admin:
        await message.answer(_("no_super_admin_rights"))
        return
    
    admins_response = await api_client._make_request('GET', 'admin/admins/')
    admins = admins_response.get('results', []) if admins_response else []
    
    if not admins:
        await message.answer(
            "🚫 Hozirda adminlar yo'q.\n\n"
            "Adminlarni Django admin panel orqali tayinlang:\n"
            "http://localhost:8000/admin/",
            reply_markup=get_super_admin_menu_keyboard()
        )
        return
    
    # Adminlar haqida batafsil ma'lumot
    admin_info = _("admins_list") + "\n" + "="*25 + "\n\n"
    
    for i, admin in enumerate(admins, 1):
        # User ma'lumotlarini olish
        user_response = await api_client._make_request('GET', f'user/users/{admin["user"]}/')
        user_info = "Noma'lum" if not user_response else f"{user_response.get('first_name', '')} {user_response.get('last_name', '')}"
        
        # Admin ticketlari
        tickets = await api_client.get_admin_tickets(admin['id'])
        ticket_count = len(tickets) if tickets else 0
        
        status = _("blocked") if admin.get('is_blocked') else _("active")
        role = admin.get('role', 'admin').title()
        
        admin_info += (
            f"{i}. {user_info}\n"
            f"   🆔 ID: {admin['id']}\n"
            f"   {_('role')}: {role}\n"
            f"   {_('status')}: {status}\n"
            f"   {_('tickets_count')}: {ticket_count} {_('ticket_count')}\n\n"
        )
    
    admin_info += f"{_('total')} {_('admins')}: {len(admins)}\n"
    admin_info += f"{_('active')}: {len([a for a in admins if not a.get('is_blocked')])}"
    
    await message.answer(admin_info, reply_markup=get_super_admin_menu_keyboard())


@router.message(F.text.in_(["📂 Kategoriyalar", "📂 Категории", "📂 Categories"]))
async def manage_categories(message: Message, is_super_admin: bool, db_user: dict):
    """Kategoriyalarni boshqarish"""
    if not is_super_admin:
        await message.answer(_("no_super_admin_rights"))
        return
    
    user_lang = db_user.get('language', 'uz')
    categories = await api_client.get_categories(lang=user_lang)
    
    if not categories:
        await message.answer(
            "🚫 Hozirda kategoriyalar yo'q.\n\n"
            "Kategoriyalarni Django admin panel orqali yarating:\n"
            "http://localhost:8000/admin/",
            reply_markup=get_super_admin_menu_keyboard()
        )
        return
    
    # Kategoriyalar haqida batafsil ma'lumot
    cat_info = _("categories_list") + "\n" + "="*30 + "\n\n"
    
    # Barcha ticketlarni olish
    all_tickets_response = await api_client._make_request('GET', 'ticket/tickets/')
    all_tickets = all_tickets_response.get('results', []) if all_tickets_response else []
    
    for i, category in enumerate(categories, 1):
        # Kategoriya bo'yicha ticketlar
        cat_tickets = [t for t in all_tickets if t.get('category') == category['id']]
        
        # Kategoriya bo'yicha adminlar
        admin_cats_response = await api_client._make_request('GET', 'admin/admin-categories/')
        admin_cats = admin_cats_response.get('results', []) if admin_cats_response else []
        category_admins = [ac for ac in admin_cats if ac.get('category') == category['id']]
        
        cat_info += (
            f"{i}. {category['name']}\n"
            f"   {_('description_short')} {category.get('description', _('no_description'))}\n"
            f"   {_('tickets_count')}: {len(cat_tickets)} {_('ticket_count')}\n"
            f"   {_('admins')}: {len(category_admins)} {_('ticket_count')}\n\n"
        )
    
    cat_info += f"{_('total')} {_('admin_categories')}: {len(categories)}"
    
    await message.answer(cat_info, reply_markup=get_super_admin_menu_keyboard())


@router.message(F.text.in_(["📊 Hisobotlar", "📊 Отчеты", "📊 Reports"]))
async def view_reports(message: Message, is_super_admin: bool, db_user: dict):
    """Hisobotlarni ko'rish"""
    if not is_super_admin:
        await message.answer(_("no_super_admin_rights"))
        return
    
    # Barcha ticketlarni olish
    all_tickets_response = await api_client._make_request('GET', 'ticket/tickets/')
    all_tickets = all_tickets_response.get('results', []) if all_tickets_response else []
    
    if not all_tickets:
        await message.answer(_("no_tickets_yet"))
        return
    
    # Vaqt bo'yicha statistika
    from datetime import date, timedelta
    today = date.today()
    yesterday_date = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    
    # Bugungi, kechagi, haftalik
    today_tickets = [t for t in all_tickets if t['created_at'].startswith(today.isoformat())]
    yesterday_tickets = [t for t in all_tickets if t['created_at'].startswith(yesterday_date.isoformat())]
    week_tickets = [t for t in all_tickets if t['created_at'] >= week_ago.isoformat()]
    
    # Status bo'yicha
    total = len(all_tickets)
    open_count = len([t for t in all_tickets if t['status'] == 'open'])
    waiting_count = len([t for t in all_tickets if t['status'] == 'waiting_admin'])
    in_progress_count = len([t for t in all_tickets if t['status'] == 'in_progress'])
    closed_count = len([t for t in all_tickets if t['status'] == 'closed'])
    
    # Kategoriya bo'yicha
    user_lang = db_user.get('language', 'uz')
    categories = await api_client.get_categories(lang=user_lang)
    category_stats = {}
    for category in categories:
        cat_tickets = [t for t in all_tickets if t['category'] == category['id']]
        category_stats[category['name']] = len(cat_tickets)
    
    # Admin bo'yicha statistika
    admins_response = await api_client._make_request('GET', 'admin/admins/')
    admins = admins_response.get('results', []) if admins_response else []
    admin_stats = {}
    for admin in admins:
        admin_tickets = [t for t in all_tickets if t.get('assigned_admin') == admin['id']]
        admin_stats[f"Admin {admin['id']}"] = len(admin_tickets)
    
    report_text = (
        f"{_('super_admin_report')}\n"
        f"{'='*30}\n\n"
        f"{_('stats_time_based')}:\n"
        f"{_('stats_today')}: {len(today_tickets)} {_('ticket_count')}\n"
        f"{_('yesterday')}: {len(yesterday_tickets)} {_('ticket_count')}\n"
        f"{_('stats_this_week')}: {len(week_tickets)} {_('ticket_count')}\n\n"
        f"{_('stats_by_status')}:\n"
        f"{_('stats_total_tickets')}: {total} {_('ticket_count')}\n"
        f"{_('stats_open')}: {open_count}\n"
        f"{_('stats_waiting')}: {waiting_count}\n"
        f"{_('stats_in_progress')}: {in_progress_count}\n"
        f"{_('stats_closed')}: {closed_count}\n\n"
        f"{_('category_by')}:\n"
    )
    
    for cat_name, count in category_stats.items():
        report_text += f"• {cat_name}: {count} ta\n"
    
    report_text += f"\n{_('admin_by')}:\n"
    for admin_name, count in admin_stats.items():
        report_text += f"• {admin_name}: {count} ta\n"
    
    # Samaradorlik
    if total > 0:
        efficiency = (closed_count / total) * 100
        report_text += f"\n{_('efficiency')}: {efficiency:.1f}%"
    
    await message.answer(report_text, reply_markup=get_super_admin_menu_keyboard())


@router.callback_query(F.data.startswith("manage_admin_"))
async def manage_specific_admin(callback: CallbackQuery, is_super_admin: bool):
    """Konkret adminni boshqarish"""
    if not is_super_admin:
        await callback.answer(_("no_super_admin_rights"))
        return
    
    admin_id = int(callback.data.split("_")[2])
    
    # Admin ma'lumotlarini olish
    admin = await api_client._make_request('GET', f'admin/admins/{admin_id}/')
    
    if not admin:
        await callback.answer(_("admin_not_found_short"))
        return
    
    # Admin ticketlarini olish
    tickets = await api_client.get_admin_tickets(admin_id)
    ticket_count = len(tickets) if tickets else 0
    
    status = _("blocked") if admin.get('is_blocked') else _("active")
    role = admin.get('role', 'admin').title()
    
    text = (
        f"👤 Admin ma'lumotlari:\n\n"
        f"🆔 ID: {admin['id']}\n"
        f"👤 User ID: {admin['user']}\n"
        f"🎭 {_('role')}: {role}\n"
        f"📊 {_('status')}: {status}\n"
        f"📋 {_('tickets_count')}: {ticket_count}\n"
        f"📅 {_('created_label')}: {admin['created_at'][:10]}"
    )
    
    # Admin boshqaruv tugmalari
    buttons = []
    
    if admin.get('is_blocked'):
        buttons.append([
            InlineKeyboardButton(
                text="🟢 Faollashtirish",
                callback_data=f"unblock_admin_{admin_id}"
            )
        ])
    else:
        buttons.append([
            InlineKeyboardButton(
                text="🔴 Bloklash",
                callback_data=f"block_admin_{admin_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text=_("back"), callback_data="back_to_admins")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data.startswith("block_admin_"))
async def block_admin(callback: CallbackQuery, is_super_admin: bool):
    """Adminni bloklash"""
    if not is_super_admin:
        await callback.answer(_("no_super_admin_rights"))
        return
    
    admin_id = int(callback.data.split("_")[2])
    
    result = await api_client._make_request(
        'PATCH', 
        f'admin/admins/{admin_id}/', 
        {'is_blocked': True}
    )
    
    if result:
        await callback.answer(_("admin_blocked"))
        # Sahifani yangilash
        await manage_specific_admin(callback, is_super_admin)
    else:
        await callback.answer(_("error_occurred"))


@router.callback_query(F.data.startswith("unblock_admin_"))
async def unblock_admin(callback: CallbackQuery, is_super_admin: bool):
    """Admin blokini ochish"""
    if not is_super_admin:
        await callback.answer(_("no_super_admin_rights"))
        return
    
    admin_id = int(callback.data.split("_")[2])
    
    result = await api_client._make_request(
        'PATCH', 
        f'admin/admins/{admin_id}/', 
        {'is_blocked': False}
    )
    
    if result:
        await callback.answer(_("admin_activated"))
        # Sahifani yangilash
        await manage_specific_admin(callback, is_super_admin)
    else:
        await callback.answer(_("error_occurred"))


@router.callback_query(F.data == "create_category")
async def create_category_start(callback: CallbackQuery, state: FSMContext, is_super_admin: bool):
    """Yangi kategoriya yaratishni boshlash"""
    if not is_super_admin:
        await callback.answer(_("no_super_admin_rights"))
        return
    
    await state.set_state(SuperAdminStates.creating_category)
    
    try:
        await callback.message.edit_text(
            _("enter_category_name"),
            reply_markup=None
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
            
    await callback.message.answer(
        _("enter_category_name"),
        reply_markup=get_admin_cancel_keyboard()
    )
    await callback.answer()


@router.message(StateFilter(SuperAdminStates.creating_category))
async def create_category_finish(message: Message, state: FSMContext, is_super_admin: bool):
    """Kategoriya yaratishni tugatish"""
    if message.text in ["❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]:
        await state.clear()
        await message.answer(
            _("category_creation_cancelled"),
            reply_markup=get_super_admin_menu_keyboard()
        )
        return
    
    category_name = message.text.strip()
    
    if not category_name:
        await message.answer(_("category_name_required"))
        return
    
    # Kategoriya yaratish
    result = await api_client._make_request(
        'POST',
        'admin/categories/',
        {
            'name_uz': category_name,
            'name_ru': category_name,
            'name_en': category_name,
            'description': f"Category: {category_name}"
        }
    )
    
    await state.clear()
    
    if result:
        await message.answer(
            _("category_created") % category_name,
            reply_markup=get_super_admin_menu_keyboard()
        )
    else:
        await message.answer(
            _("category_creation_failed"),
            reply_markup=get_super_admin_menu_keyboard()
        )


@router.message(F.text.in_(["📈 Statistika", "📈 Статистика", "📈 Statistics"]))
async def detailed_statistics(message: Message, is_super_admin: bool, db_user: dict):
    """Batafsil statistika"""
    if not is_super_admin:
        await message.answer(_("no_super_admin_rights"))
        return
    
    # Barcha ma'lumotlarni olish
    all_tickets_response = await api_client._make_request('GET', 'ticket/tickets/')
    all_tickets = all_tickets_response.get('results', []) if all_tickets_response else []
    
    admins_response = await api_client._make_request('GET', 'admin/admins/')
    admins = admins_response.get('results', []) if admins_response else []
    
    users_response = await api_client._make_request('GET', 'user/users/')
    users = users_response.get('results', []) if users_response else []
    
    user_lang = db_user.get('language', 'uz')
    categories = await api_client.get_categories(lang=user_lang)
    
    # Vaqt bo'yicha
    from datetime import date, timedelta
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    today_tickets = [t for t in all_tickets if t['created_at'].startswith(today.isoformat())]
    week_tickets = [t for t in all_tickets if t['created_at'] >= week_ago.isoformat()]
    month_tickets = [t for t in all_tickets if t['created_at'] >= month_ago.isoformat()]
    
    # Status statistikasi
    status_stats = {}
    for status in ['open', 'waiting_admin', 'in_progress', 'closed']:
        status_stats[status] = len([t for t in all_tickets if t.get('status') == status])
    
    # Admin samaradorligi
    admin_efficiency = {}
    for admin in admins:
        admin_tickets = [t for t in all_tickets if t.get('assigned_admin') == admin['id']]
        total = len(admin_tickets)
        closed = len([t for t in admin_tickets if t.get('status') == 'closed'])
        efficiency = (closed / total * 100) if total > 0 else 0
        admin_efficiency[admin['id']] = {'total': total, 'closed': closed, 'efficiency': efficiency}
    
    stats_text = (
        f"📈 {_('detailed_statistics')}\n"
        f"{'='*35}\n\n"
        f"{_('stats_general')}:\n"
        f"{_('stats_total_users')}: {len(users)}\n"
        f"{_('stats_total_admins')}: {len(admins)}\n"
        f"{_('stats_total_categories')}: {len(categories)}\n"
        f"{_('stats_total_tickets')}: {len(all_tickets)}\n\n"
        f"{_('stats_time_based')}:\n"
        f"{_('stats_today')}: {len(today_tickets)} {_('ticket_count')}\n"
        f"{_('stats_this_week')}: {len(week_tickets)} {_('ticket_count')}\n"
        f"{_('stats_this_month')}: {len(month_tickets)} {_('ticket_count')}\n\n"
        f"{_('stats_by_status')}:\n"
        f"{_('stats_open')}: {status_stats.get('open', 0)}\n"
        f"{_('stats_waiting')}: {status_stats.get('waiting_admin', 0)}\n"
        f"{_('stats_in_progress')}: {status_stats.get('in_progress', 0)}\n"
        f"{_('stats_closed')}: {status_stats.get('closed', 0)}\n\n"
        f"{_('stats_top_admins')}:\n"
    )
    
    # Top 3 admin
    sorted_admins = sorted(admin_efficiency.items(), key=lambda x: x[1]['total'], reverse=True)[:3]
    for i, (admin_id, stats) in enumerate(sorted_admins, 1):
        stats_text += f"{i}. Admin {admin_id}: {stats['total']} ta ({stats['efficiency']:.1f}%)\n"
    
    await message.answer(stats_text, reply_markup=get_super_admin_menu_keyboard())


@router.message(F.text.in_(["🔧 Tizim", "🔧 Система", "🔧 System"]))
async def system_info(message: Message, is_super_admin: bool):
    """Tizim ma'lumotlari"""
    if not is_super_admin:
        await message.answer(_("no_super_admin_rights"))
        return
    
    import psutil
    from datetime import datetime
    
    # Tizim ma'lumotlari
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    system_text = (
        f"{_('system_info_title')}\n"
        f"{'='*25}\n\n"
        f"{_('server')}:\n"
        f"{_('cpu')}: {cpu_percent}%\n"
        f"{_('ram')}: {memory.percent}% ({memory.used // 1024**3}GB / {memory.total // 1024**3}GB)\n"
        f"{_('disk')}: {disk.percent}% ({disk.used // 1024**3}GB / {disk.total // 1024**3}GB)\n\n"
        f"{_('bot')}:\n"
        f"{_('status')}: {_('active')}\n"
        f"{_('uptime')}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"{_('database')}:\n"
        f"{_('type')}: SQLite\n"
        f"{_('status')}: {_('connected')}\n\n"
        f"{_('api')}:\n"
        f"• Django: http://localhost:8000\n"
        f"• Admin: http://localhost:8000/admin/\n"
        f"{_('status')}: {_('running')}"
    )
    
    await message.answer(system_text, reply_markup=get_super_admin_menu_keyboard())


@router.message(F.text.in_(["👤 User rejimi", "👤 Режим пользователя", "👤 User mode"]))
async def switch_to_user_mode_super(message: Message):
    """User rejimiga o'tish"""
    await message.answer(
        _("super_admin_user_mode") + "\n\n" + _("admin_menu_text"),
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text.in_(["👨‍💼 Admin rejimi", "👨‍💼 Режим администратора", "👨‍💼 Admin mode"]))
async def switch_to_admin_mode_super(message: Message, admin: dict):
    """Admin rejimiga o'tish"""
    if not admin:
        await message.answer(_("admin_not_found"))
        return
    
    await message.answer(
        _("super_admin_admin_mode") + "\n\n" + _("admin_menu_text"),
        reply_markup=get_admin_main_menu_keyboard()
    )


@router.callback_query(F.data == "back_to_admins")
async def back_to_admins_list(callback: CallbackQuery, is_super_admin: bool):
    """Adminlar ro'yxatiga qaytish"""
    if not is_super_admin:
        await callback.answer(_("no_super_admin_rights"))
        return
    
    admins_response = await api_client._make_request('GET', 'admin/admins/')
    admins = admins_response.get('results', []) if admins_response and isinstance(admins_response, dict) else (admins_response if isinstance(admins_response, list) else [])
    
    try:
        await callback.message.edit_text(
            f"{_('admins_list')} ({len(admins)}):",
            reply_markup=get_admins_management_keyboard(admins)
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "super_admin_menu")
async def back_to_super_admin_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Super admin menyusiga qaytish"""
    await state.clear()
    try:
        await callback.message.edit_text(
            "👑 Super Admin Panel",
            reply_markup=get_super_admin_menu_keyboard()
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()
