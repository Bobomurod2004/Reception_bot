from rest_framework import viewsets
from .models import Admin, Category, AdminCategory, AdminActivity
from .serializers import (
    AdminSerializer,
    CategorySerializer,
    AdminCategorySerializer,
    AdminActivitySerializer,
)


class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        """Return only active categories, ordered by 'order' field"""
        return Category.objects.filter(is_active=True).order_by('order', 'id')
    
    def get_serializer_context(self):
        """Pass request to serializer for language detection"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class AdminCategoryViewSet(viewsets.ModelViewSet):
    queryset = AdminCategory.objects.all()
    serializer_class = AdminCategorySerializer


class AdminActivityViewSet(viewsets.ModelViewSet):
    queryset = AdminActivity.objects.all()
    serializer_class = AdminActivitySerializer
