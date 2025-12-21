"""
Translation dictionary for multi-language support
"""
#flake8: noqa
from typing import Dict

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'uz': {
        # User messages
        'welcome_user': '👋 Salom, {name}!\n\n🤖 Men sizning savollaringizga javob berishga yordam beradigan support botman.\n\n📝 Savol berish uchun "Yangi savol" tugmasini bosing\n📋 Mavjud savollaringizni ko\'rish uchun "Mening savollarim" tugmasini bosing\n\nQuyidagi tugmalardan birini tanlang:',
        'welcome_admin': '👨‍💼 Salom, Admin {name}!\n\nSizda admin huquqlari mavjud.\n\nQuyidagi tugmalardan birini tanlang:',
        'welcome_super_admin': '👑 Salom, Super Admin {name}!\n\nSizda barcha tizim boshqaruv huquqlari mavjud.\n\n🔧 Super Admin rejimi: /superadmin\n👨‍💼 Admin rejimi: /admin\n👤 User rejimi: Quyidagi tugmalar',
        'new_question': '📝 Yangi savol',
        'my_questions': '📋 Mening savollarim',
        'help': 'ℹ️ Yordam',
        'select_category': '📁 Kategoriyani tanlang:',
        'write_question': '💬 Savolingizni yozing:',
        'cancel': '❌ Bekor qilish',
        'question_sent': '✅ Savolingiz yuborildi! Admin javobini kuting.',
        'no_open_tickets': '✅ Hozircha ochiq savollar yo\'q.',
        'ticket_status_open': '🟢 Ochiq',
        'ticket_status_waiting': '🟡 Admin kutilmoqda',
        'ticket_status_in_progress': '🔵 Jarayonda',
        'ticket_status_closed': '🔴 Yopiq',
        'ticket_priority_low': '🟢 Past',
        'ticket_priority_medium': '🟡 O\'rta',
        'ticket_priority_high': '🔴 Yuqori',
        'admin_replied': '✅ Admin javob berdi:',
        'no_response_4h': '⏰ 4 soatdan ortiq vaqt o\'tdi, yangi savol yubora olasiz.',
        'can_send_new': '✅ Yangi savol yubora olasiz.',
        
        # Admin messages
        'admin_no_tickets': '✅ Hozircha sizga biriktirilgan savollar yo\'q.\n\nYangi savollar kelganda sizga bildirishnoma yuboriladi.',
        'admin_all_done': '✅ Barcha savollar hal qilindi!\n\nYangi savollar kelganda sizga bildirishnoma yuboriladi.',
        'admin_my_tickets': '📋 Sizning ticketlaringiz ({count} ta):',
        'admin_reply_prompt': '💬 Javobingizni yozing:',
        'admin_ticket_closed': '✅ Ticket yopildi!',
        'admin_statistics': '📊 Statistika',
        'admin_settings': '⚙️ Sozlamalar',
        'admin_user_mode': '👤 User rejimi',
        'admin_not_found': '❌ Admin profili topilmadi.',
        
        # Language selection
        'select_language': '🌐 Tilni tanlang / Select language / Выберите язык:',
        'language_set': '✅ Til o\'zgartirildi: {lang}',
        'error_occurred': '❌ Xatolik yuz berdi.',
        'try_start': 'Qaytadan /start bosing.',
    },
    'ru': {
        # User messages
        'welcome_user': '👋 Здравствуйте, {name}!\n\n🤖 Я бот поддержки, который поможет ответить на ваши вопросы.\n\n📝 Чтобы задать вопрос, нажмите "Новый вопрос"\n📋 Чтобы посмотреть ваши вопросы, нажмите "Мои вопросы"\n\nВыберите одну из кнопок ниже:',
        'welcome_admin': '👨‍💼 Здравствуйте, Админ {name}!\n\nУ вас есть права администратора.\n\nВыберите одну из кнопок ниже:',
        'welcome_super_admin': '👑 Здравствуйте, Супер Админ {name}!\n\nУ вас есть все права управления системой.\n\n🔧 Режим Супер Админа: /superadmin\n👨‍💼 Режим Админа: /admin\n👤 Режим Пользователя: Кнопки ниже',
        'new_question': '📝 Новый вопрос',
        'my_questions': '📋 Мои вопросы',
        'help': 'ℹ️ Помощь',
        'select_category': '📁 Выберите категорию:',
        'write_question': '💬 Напишите ваш вопрос:',
        'cancel': '❌ Отмена',
        'question_sent': '✅ Ваш вопрос отправлен! Ожидайте ответа администратора.',
        'no_open_tickets': '✅ Пока нет открытых вопросов.',
        'ticket_status_open': '🟢 Открыт',
        'ticket_status_waiting': '🟡 Ожидает админа',
        'ticket_status_in_progress': '🔵 В процессе',
        'ticket_status_closed': '🔴 Закрыт',
        'ticket_priority_low': '🟢 Низкий',
        'ticket_priority_medium': '🟡 Средний',
        'ticket_priority_high': '🔴 Высокий',
        'admin_replied': '✅ Админ ответил:',
        'no_response_4h': '⏰ Прошло более 4 часов, вы можете отправить новый вопрос.',
        'can_send_new': '✅ Вы можете отправить новый вопрос.',
        
        # Admin messages
        'admin_no_tickets': '✅ Пока нет вопросов, назначенных вам.\n\nКогда появятся новые вопросы, вам будет отправлено уведомление.',
        'admin_all_done': '✅ Все вопросы решены!\n\nКогда появятся новые вопросы, вам будет отправлено уведомление.',
        'admin_my_tickets': '📋 Ваши тикеты ({count} шт.):',
        'admin_reply_prompt': '💬 Напишите ваш ответ:',
        'admin_ticket_closed': '✅ Тикет закрыт!',
        'admin_statistics': '📊 Статистика',
        'admin_settings': '⚙️ Настройки',
        'admin_user_mode': '👤 Режим пользователя',
        
        # Language selection
        'select_language': '🌐 Выберите язык / Select language / Tilni tanlang:',
        'language_set': '✅ Язык изменен: {lang}',
        'error_occurred': '❌ Произошла ошибка.',
        'try_start': 'Попробуйте снова /start.',
    },
    'en': {
        # User messages
        'welcome_user': '👋 Hello, {name}!\n\n🤖 I am a support bot that will help answer your questions.\n\n📝 To ask a question, press "New question"\n📋 To view your questions, press "My questions"\n\nSelect one of the buttons below:',
        'welcome_admin': '👨‍💼 Hello, Admin {name}!\n\nYou have administrator rights.\n\nSelect one of the buttons below:',
        'welcome_super_admin': '👑 Hello, Super Admin {name}!\n\nYou have all system management rights.\n\n🔧 Super Admin mode: /superadmin\n👨‍💼 Admin mode: /admin\n👤 User mode: Buttons below',
        'new_question': '📝 New question',
        'my_questions': '📋 My questions',
        'help': 'ℹ️ Help',
        'select_category': '📁 Select category:',
        'write_question': '💬 Write your question:',
        'cancel': '❌ Cancel',
        'question_sent': '✅ Your question has been sent! Wait for admin response.',
        'no_open_tickets': '✅ No open questions yet.',
        'ticket_status_open': '🟢 Open',
        'ticket_status_waiting': '🟡 Waiting for admin',
        'ticket_status_in_progress': '🔵 In progress',
        'ticket_status_closed': '🔴 Closed',
        'ticket_priority_low': '🟢 Low',
        'ticket_priority_medium': '🟡 Medium',
        'ticket_priority_high': '🔴 High',
        'admin_replied': '✅ Admin replied:',
        'no_response_4h': '⏰ More than 4 hours have passed, you can send a new question.',
        'can_send_new': '✅ You can send a new question.',
        
        # Admin messages
        'admin_no_tickets': '✅ No questions assigned to you yet.\n\nWhen new questions arrive, you will be notified.',
        'admin_all_done': '✅ All questions resolved!\n\nWhen new questions arrive, you will be notified.',
        'admin_my_tickets': '📋 Your tickets ({count}):',
        'admin_reply_prompt': '💬 Write your reply:',
        'admin_ticket_closed': '✅ Ticket closed!',
        'admin_statistics': '📊 Statistics',
        'admin_settings': '⚙️ Settings',
        'admin_user_mode': '👤 User mode',
        
        # Language selection
        'select_language': '🌐 Select language / Выберите язык / Tilni tanlang:',
        'language_set': '✅ Language changed: {lang}',
        'error_occurred': '❌ An error occurred.',
        'try_start': 'Try /start again.',
    }
}


def get_text(key: str, lang: str = 'uz', **kwargs) -> str:
    """Get translated text"""
    if lang not in TRANSLATIONS:
        lang = 'uz'
    
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS['uz'].get(key, key))
    
    # Format with kwargs if provided
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    
    return text


def get_language_name(lang: str) -> str:
    """Get language name"""
    names = {
        'uz': 'O\'zbek',
        'ru': 'Русский',
        'en': 'English'
    }
    return names.get(lang, 'O\'zbek')

