"""
API permissions for ticket views
"""
from rest_framework import permissions
from rest_framework.request import Request
from .models import Ticket


class IsAdminOrReadOnly(permissions.BasePermission):
    """Admin uchun yozish huquqi, boshqalar uchun faqat o'qish"""
    
    def has_permission(self, request: Request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Token tekshirish (API_TOKEN)
        api_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from django.conf import settings
        expected_token = getattr(settings, 'API_TOKEN', None)
        return api_token == expected_token


class IsTicketOwner(permissions.BasePermission):
    """Ticket egasi yoki biriktirilgan admin"""
    
    def has_object_permission(self, request: Request, view, obj: Ticket):
        # Token tekshirish
        api_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        from django.conf import settings
        expected_token = getattr(settings, 'API_TOKEN', None)
        if api_token != expected_token:
            return False
        
        # Admin ID query parametridan olinadi
        admin_id = request.query_params.get('admin_id')
        if admin_id:
            try:
                admin_id = int(admin_id)
                return obj.assigned_admin_id == admin_id
            except (ValueError, TypeError):
                return False
        
        # User ID query parametridan olinadi
        user_id = request.query_params.get('user_id')
        if user_id:
            try:
                user_id = int(user_id)
                return obj.user_id == user_id
            except (ValueError, TypeError):
                return False
        
        return False

