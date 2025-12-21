from rest_framework import serializers
from .models import Admin, Category, AdminCategory, AdminActivity


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'is_active', 'order', 'created_at']
    
    def get_name(self, obj):
        """Return category name based on requested language"""
        request = self.context.get('request')
        lang = request.query_params.get('lang', 'uz') if request else 'uz'
        
        # Ensure lang is one of uz, ru, en
        if lang not in ['uz', 'ru', 'en']:
            lang = 'uz'
        
        return getattr(obj, f'name_{lang}', obj.name_uz)


class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminCategory
        fields = '__all__'


class AdminActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminActivity
        fields = '__all__'
