"""
Django signals for ticket events - Real-time push notifications
"""
import logging
import threading
import requests
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Ticket, Message

logger = logging.getLogger(__name__)

# Bot token .env dan olinadi
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_telegram_message(chat_id: int, text: str, reply_markup: dict = None):
    """Telegram'ga xabar yuborish"""
    try:
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        if reply_markup:
            data['reply_markup'] = reply_markup
        
        response = requests.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            return True
        else:
            logger.warning(f"Telegram API xatosi: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Telegram xabar yuborishda xatolik: {e}")
        return False


def notify_admin_new_ticket_async(ticket_id: int, admin_telegram_id: int):
    """Admin'ga yangi ticket haqida xabar yuborish (async)"""
    def send_notification():
        try:
            # Ticket ma'lumotlarini olish
            from apps.ticket.models import Ticket
            from apps.ticket.serializers import TicketSerializer
            
            try:
                ticket = Ticket.objects.select_related('user', 'category', 'assigned_admin__user').get(id=ticket_id)
                serializer = TicketSerializer(ticket)
                ticket_data = serializer.data
                
                # Ticket xabarlarini olish
                from apps.ticket.models import Message
                messages = Message.objects.filter(ticket=ticket).order_by('timestamp')
                first_message = messages.first() if messages.exists() else None
                
                if not first_message:
                    return
                
                # Xabar matni
                ticket_number = ticket_data.get('ticket_number', f"#{ticket_id}")
                category_name = ticket.category.name_uz if ticket.category else 'Noma\'lum'
                user_name = ticket.user.first_name or 'Foydalanuvchi'
                content = first_message.content or ''
                content_type = first_message.content_type
                file_id = first_message.file
                
                text = (
                    f"🆕 **Yangi savol kelib tushdi!**\n\n"
                    f"📋 Ticket: `{ticket_number}`\n"
                    f"📁 Kategoriya: {category_name}\n"
                    f"👤 Foydalanuvchi: {user_name}\n"
                    f"📝 Savol:\n\n{content[:500]}"
                )
                
                # Inline keyboard
                reply_markup = {
                    'inline_keyboard': [
                        [
                            {'text': '💬 Javob berish', 'callback_data': f'admin_reply_{ticket_id}'}
                        ],
                        [
                            {'text': '✅ Yopish', 'callback_data': f'admin_close_{ticket_id}'}
                        ]
                    ]
                }
                
                # Media yuborish
                if content_type == 'image' and file_id:
                    requests.post(
                        f"{TELEGRAM_API_URL}/sendPhoto",
                        json={
                            'chat_id': admin_telegram_id,
                            'photo': file_id,
                            'caption': text,
                            'reply_markup': reply_markup,
                            'parse_mode': 'Markdown'
                        },
                        timeout=10
                    )
                elif content_type == 'video' and file_id:
                    requests.post(
                        f"{TELEGRAM_API_URL}/sendVideo",
                        json={
                            'chat_id': admin_telegram_id,
                            'video': file_id,
                            'caption': text,
                            'reply_markup': reply_markup,
                            'parse_mode': 'Markdown'
                        },
                        timeout=10
                    )
                elif content_type == 'audio' and file_id:
                    requests.post(
                        f"{TELEGRAM_API_URL}/sendAudio",
                        json={
                            'chat_id': admin_telegram_id,
                            'audio': file_id,
                            'caption': text,
                            'reply_markup': reply_markup,
                            'parse_mode': 'Markdown'
                        },
                        timeout=10
                    )
                elif content_type == 'file' and file_id:
                    requests.post(
                        f"{TELEGRAM_API_URL}/sendDocument",
                        json={
                            'chat_id': admin_telegram_id,
                            'document': file_id,
                            'caption': text,
                            'reply_markup': reply_markup,
                            'parse_mode': 'Markdown'
                        },
                        timeout=10
                    )
                else:
                    # Oddiy text xabar
                    send_telegram_message(admin_telegram_id, text, reply_markup)
                
                logger.info(f"Admin {admin_telegram_id} ga yangi ticket {ticket_id} haqida xabar yuborildi")
                
            except Ticket.DoesNotExist:
                logger.error(f"Ticket {ticket_id} topilmadi")
            except Exception as e:
                logger.error(f"Ticket ma'lumotlarini olishda xatolik: {e}", exc_info=True)
                
        except Exception as e:
            logger.error(f"Admin'ga xabar yuborishda xatolik: {e}", exc_info=True)
    
    # Asinxron yuborish
    thread = threading.Thread(target=send_notification)
    thread.daemon = True
    thread.start()


def notify_user_admin_replied_async(ticket_id: int, user_telegram_id: int):
    """User'ga admin javobi haqida xabar yuborish (async)"""
    def send_notification():
        try:
            from apps.ticket.models import Ticket, Message
            
            try:
                ticket = Ticket.objects.get(id=ticket_id)
                messages = Message.objects.filter(ticket=ticket).order_by('-timestamp')
                
                # Admin javobini topish
                admin_message = None
                for msg in messages:
                    if msg.sender_admin:
                        admin_message = msg
                        break
                
                if not admin_message:
                    return
                
                content = admin_message.content or ''
                content_type = admin_message.content_type
                file_id = admin_message.file
                
                text = f"✅ **Admin javob berdi:**\n\n{content[:500]}"
                
                # Media yuborish
                if content_type == 'image' and file_id:
                    requests.post(
                        f"{TELEGRAM_API_URL}/sendPhoto",
                        json={
                            'chat_id': user_telegram_id,
                            'photo': file_id,
                            'caption': text,
                            'parse_mode': 'Markdown'
                        },
                        timeout=10
                    )
                elif content_type == 'video' and file_id:
                    requests.post(
                        f"{TELEGRAM_API_URL}/sendVideo",
                        json={
                            'chat_id': user_telegram_id,
                            'video': file_id,
                            'caption': text,
                            'parse_mode': 'Markdown'
                        },
                        timeout=10
                    )
                elif content_type == 'audio' and file_id:
                    requests.post(
                        f"{TELEGRAM_API_URL}/sendAudio",
                        json={
                            'chat_id': user_telegram_id,
                            'audio': file_id,
                            'caption': text,
                            'parse_mode': 'Markdown'
                        },
                        timeout=10
                    )
                elif content_type == 'file' and file_id:
                    requests.post(
                        f"{TELEGRAM_API_URL}/sendDocument",
                        json={
                            'chat_id': user_telegram_id,
                            'document': file_id,
                            'caption': text,
                            'parse_mode': 'Markdown'
                        },
                        timeout=10
                    )
                else:
                    send_telegram_message(user_telegram_id, text)
                
                logger.info(f"User {user_telegram_id} ga admin javobi haqida xabar yuborildi")
                
            except Ticket.DoesNotExist:
                logger.error(f"Ticket {ticket_id} topilmadi")
            except Exception as e:
                logger.error(f"Ticket ma'lumotlarini olishda xatolik: {e}", exc_info=True)
                
        except Exception as e:
            logger.error(f"User'ga xabar yuborishda xatolik: {e}", exc_info=True)
    
    # Asinxron yuborish
    thread = threading.Thread(target=send_notification)
    thread.daemon = True
    thread.start()


@receiver(post_save, sender=Ticket)
def ticket_created_or_updated(sender, instance, created, **kwargs):
    """Ticket yaratilganda yoki yangilanganda - Real-time push"""
    if created:
        # Yangi ticket yaratildi
        if instance.assigned_admin:
            # Admin biriktirilgan bo'lsa, unga xabar yuborish
            admin = instance.assigned_admin
            user = admin.user
            if user and user.telegram_id:
                notify_admin_new_ticket_async(
                    ticket_id=instance.id,
                    admin_telegram_id=user.telegram_id
                )
                logger.info(f"Ticket {instance.ticket_number} admin {admin.id} ga biriktirildi - push notification yuborildi")


@receiver(post_save, sender=Message)
def message_created(sender, instance, created, **kwargs):
    """Message yaratilganda - Real-time push"""
    if created:
        ticket = instance.ticket
        
        # Agar admin javob bergan bo'lsa, userga xabar yuborish
        if instance.sender_admin:
            user = ticket.user
            if user and user.telegram_id:
                notify_user_admin_replied_async(
                    ticket_id=ticket.id,
                    user_telegram_id=user.telegram_id
                )
                logger.info(f"User {user.telegram_id} ga admin javobi haqida push notification yuborildi")
        
        # Agar user savol yuborgan bo'lsa, adminlarga xabar yuborish
        elif instance.sender_user:
            if ticket.assigned_admin:
                admin = ticket.assigned_admin
                user = admin.user
                if user and user.telegram_id:
                    notify_admin_new_ticket_async(
                        ticket_id=ticket.id,
                        admin_telegram_id=user.telegram_id
                    )
                    logger.info(f"Admin {user.telegram_id} ga user javobi haqida push notification yuborildi")

