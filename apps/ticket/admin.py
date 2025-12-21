from django.contrib import admin
from apps.ticket.models import Ticket, Message, AdminActivityLog


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'title', 'user', 'category',
                    'status', 'priority', 'assigned_admin', 'is_read',
                    'read_at', 'close_at')
    search_fields = ('ticket_number', 'title', 'user__username',
                     'assigned_admin__user__username')
    list_filter = ('status', 'priority', 'category')
    ordering = ('-created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'sender_user', 'sender_admin',
                    "content", 'created_at')
    search_fields = ('ticket__ticket_number', 'sender_user__username',
                     'sender_admin__user__username', 'content')
    ordering = ('-created_at',)


@admin.register(AdminActivityLog)
class AdminActivityLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action', 'created_at')
    search_fields = ('admin__user__username', 'action')
    ordering = ('-created_at',)
