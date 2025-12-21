from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _
from typing import List, Dict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_admin_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Admin asosiy menyu klaviaturasi"""
    keyboard = [
        [KeyboardButton(text=_("admin_my_tickets"))],
        [KeyboardButton(text=_("admin_statistics")), KeyboardButton(text=_("admin_settings"))],
        [KeyboardButton(text=_("admin_user_mode"))]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_admin_tickets_keyboard(tickets: List[Dict], current_filter: str = 'today') -> InlineKeyboardMarkup:
    """Admin ticketlari klaviaturasi (geografik sana filtr bilan)"""
    buttons = []
    from datetime import datetime, timedelta
    
    # 1. Asosiy filtrlar (Bugun, Kecha, Eskilar)
    filter_row = [
        InlineKeyboardButton(
            text=f"{'✅ ' if current_filter == 'today' else ''}{_('filter_today')}",
            callback_data="admin_filter_today"
        ),
        InlineKeyboardButton(
            text=f"{'✅ ' if current_filter == 'yesterday' else ''}{_('filter_yesterday')}",
            callback_data="admin_filter_yesterday"
        ),
        InlineKeyboardButton(
            text=f"{'✅ ' if current_filter == 'old' else ''}{_('filter_old')}",
            callback_data="admin_filter_old"
        )
    ]
    buttons.append(filter_row)
    
    # 2. Sana navigatsiyasi (< YYYY-MM-DD >)
    now = datetime.now()
    if current_filter == 'today':
        target_date = now.date()
    elif current_filter == 'yesterday':
        target_date = (now - timedelta(days=1)).date()
    elif '-' in current_filter:
        try:
            target_date = datetime.strptime(current_filter, '%Y-%m-%d').date()
        except ValueError:
            target_date = now.date()
    else:
        target_date = None

    if target_date:
        prev_date = (target_date - timedelta(days=1)).strftime('%Y-%m-%d')
        next_date = (target_date + timedelta(days=1)).strftime('%Y-%m-%d')
        
        nav_row = [
            InlineKeyboardButton(text="◀️", callback_data=f"admin_filter_{prev_date}"),
            InlineKeyboardButton(text=f"📅 {target_date.strftime('%d.%m')}", callback_data="admin_pick_date"),
            InlineKeyboardButton(text="▶️", callback_data=f"admin_filter_{next_date}")
        ]
        buttons.append(nav_row)
    else:
        buttons.append([
            InlineKeyboardButton(text=f"📅 {_('filter_pick_date')}", callback_data="admin_pick_date")
        ])
    
    for ticket in tickets:
        status_emoji = {
            'open': '🟢',
            'waiting_admin': '🟡',
            'in_progress': '🔵',
            'closed': '🔴'
        }.get(ticket['status'], '⚪')
        
        priority_emoji = {
            'low': '🟢',
            'medium': '🟡', 
            'high': '🔴'
        }.get(ticket['priority'], '⚪')
        
        buttons.append([
            InlineKeyboardButton(
                text=f"{status_emoji}{priority_emoji} {ticket['title'][:25]}...",
                callback_data=f"admin_ticket_{ticket['id']}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text=_("refresh"), callback_data=f"refresh_admin_tickets_{current_filter}")
    ])
    buttons.append([
        InlineKeyboardButton(text=_("back_to_menu"), callback_data="admin_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_ticket_admin_actions_keyboard(ticket_id: int) -> InlineKeyboardMarkup:
    """Ticket admin harakatlari klaviaturasi"""
    buttons = [
        [
            InlineKeyboardButton(
                text=_("reply"),
                callback_data=f"admin_reply_{ticket_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=_("in_progress"),
                callback_data=f"admin_progress_{ticket_id}"
            ),
            InlineKeyboardButton(
                text=_("close"),
                callback_data=f"admin_close_{ticket_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=_("messages"),
                callback_data=f"admin_messages_{ticket_id}"
            )
        ],
        [
            InlineKeyboardButton(text=_("back"), callback_data="admin_tickets")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_super_admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """Super admin menyu klaviaturasi"""
    keyboard = [
        [KeyboardButton(text=_("super_admin_admins")), KeyboardButton(text=_("super_admin_categories"))],
        [KeyboardButton(text=_("super_admin_reports")), KeyboardButton(text=_("super_admin_statistics"))],
        [KeyboardButton(text=_("super_admin_system")), KeyboardButton(text=_("super_admin_settings"))],
        [KeyboardButton(text=_("super_admin_user_mode")), KeyboardButton(text=_("super_admin_admin_mode"))]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_admins_management_keyboard(admins: List[Dict]) -> InlineKeyboardMarkup:
    """Adminlar boshqaruv klaviaturasi"""
    buttons = []
    
    for admin in admins:
        status = "🔴" if admin.get('is_blocked') else "🟢"
        role = admin.get('role', 'admin')
        
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {role} - ID:{admin['id']}",
                callback_data=f"manage_admin_{admin['id']}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="➕ Yangi admin", callback_data="create_admin")
    ])
    buttons.append([
        InlineKeyboardButton(text=_("back"), callback_data="super_admin_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_categories_management_keyboard(categories: List[Dict]) -> InlineKeyboardMarkup:
    """Kategoriyalar boshqaruv klaviaturasi"""
    buttons = []
    
    for category in categories:
        buttons.append([
            InlineKeyboardButton(
                text=f"📂 {category['name']}",
                callback_data=f"manage_category_{category['id']}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="➕ Yangi kategoriya", callback_data="create_category")
    ])
    buttons.append([
        InlineKeyboardButton(text=_("back"), callback_data="super_admin_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Admin bekor qilish klaviaturasi"""
    keyboard = [
        [KeyboardButton(text=_("cancel"))]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
