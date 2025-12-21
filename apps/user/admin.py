from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'telegram_id', 'username', 'first_name', 'last_name', 'is_blocked', 'created_at']
    list_filter = ['is_blocked', 'created_at']
    search_fields = ['telegram_id', 'username', 'first_name', 'last_name']
    list_editable = ['is_blocked']
    readonly_fields = ['telegram_id', 'created_at', 'updated_at']
