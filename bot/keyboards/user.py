from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _
from typing import List, Dict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi"""
    keyboard = [
        [KeyboardButton(text=_("new_question"))],
        [KeyboardButton(text=_("my_questions"))],
        [KeyboardButton(text=_("help")), KeyboardButton(text=_("settings"))]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_settings_keyboard() -> ReplyKeyboardMarkup:
    """Sozlamalar klaviaturasi"""
    keyboard = [
        [KeyboardButton(text=_("language_button"))],
        [KeyboardButton(text=_("back_to_menu"))]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_categories_keyboard(categories: List[Dict]) -> InlineKeyboardMarkup:
    """Kategoriyalar klaviaturasi"""
    buttons = []
    
    for category in categories:
        buttons.append([
            InlineKeyboardButton(
                text=category['name'],
                callback_data=f"category_{category['id']}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text=_("back"), callback_data="back_to_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_ticket_actions_keyboard(ticket_id: int) -> InlineKeyboardMarkup:
    """Ticket harakatlari klaviaturasi"""
    buttons = [
        [
            InlineKeyboardButton(
                text=_("reply"),
                callback_data=f"write_message_{ticket_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text=_("close"),
                callback_data=f"close_ticket_{ticket_id}"
            )
        ],
        [
            InlineKeyboardButton(text=_("back"), callback_data="my_tickets")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_my_tickets_keyboard(tickets: List[Dict]) -> InlineKeyboardMarkup:
    """Mening ticketlarim klaviaturasi"""
    buttons = []
    
    for ticket in tickets:
        status_emoji = {
            'open': '🟢',
            'waiting_admin': '🟡',
            'in_progress': '🔵',
            'closed': '🔴'
        }.get(ticket['status'], '⚪')
        
        buttons.append([
            InlineKeyboardButton(
                text=f"{status_emoji} {ticket['title'][:30]}...",
                callback_data=f"ticket_{ticket['id']}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text=_("back_to_menu"), callback_data="back_to_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_priority_keyboard() -> InlineKeyboardMarkup:
    """Muhimlik darajasi klaviaturasi"""
    buttons = [
        [
            InlineKeyboardButton(text="🟢 Past", callback_data="priority_low"),
            InlineKeyboardButton(text="🟡 O'rta", callback_data="priority_medium")
        ],
        [
            InlineKeyboardButton(text="🔴 Yuqori", callback_data="priority_high")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_categories")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish klaviaturasi"""
    keyboard = [
        [KeyboardButton(text=_("cancel"))]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )
