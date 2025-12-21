from django.contrib import admin
from .models import Admin, Category, AdminCategory, AdminActivity


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_username', 'get_telegram_id', 'role',
                    'is_blocked', 'created_at']
    list_filter = ['role', 'is_blocked', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__telegram_id']
    list_editable = ['role', 'is_blocked']

    def get_username(self, obj):
        return obj.user.username or f"User_{obj.user.telegram_id}"
    get_username.short_description = 'Username'

    def get_telegram_id(self, obj):
        return obj.user.telegram_id
    get_telegram_id.short_description = 'Telegram ID'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_uz', 'name_ru', 'name_en', 'is_active', 'order', 'get_admin_count', 'created_at']
    search_fields = ['name_uz', 'name_ru', 'name_en', 'description']
    list_editable = ['name_uz', 'name_ru', 'name_en', 'is_active', 'order']
    list_filter = ['is_active', 'created_at']
    ordering = ['order', 'id']

    def get_admin_count(self, obj):
        return obj.admins.count()
    get_admin_count.short_description = 'Admin soni'


@admin.register(AdminCategory)
class AdminCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_admin_name', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['admin__user__username', 'category__name_uz']

    def get_admin_name(self, obj):
        return obj.admin.user.username or f"User_{obj.admin.user.telegram_id}"
    get_admin_name.short_description = 'Admin'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('admin__user',
                                                            'category')


@admin.register(AdminActivity)
class AdminActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_admin_name', 'date', 'assigned_tickets',
                    'answered_tickets', 'pending_tickets']
    list_filter = ['date', 'admin']
    search_fields = ['admin__user__username']
    readonly_fields = ['date']

    def get_admin_name(self, obj):
        return obj.admin.user.username or f"User_{obj.admin.user.telegram_id}"
    get_admin_name.short_description = 'Admin'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('admin__user')
