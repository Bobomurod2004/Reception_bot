"""
Language selection keyboards
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard"""
    buttons = [
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
