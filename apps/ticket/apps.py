from django.apps import AppConfig


class TicketConfig(AppConfig):
    name = 'apps.ticket'
    
    def ready(self):
        """Signal'larni ro'yxatdan o'tkazish"""
        import apps.ticket.signals  # noqa