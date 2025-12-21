"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/admin/', include('apps.admin.api_urls')),
    path('api/ticket/', include('apps.ticket.api_urls')),
    path('api/user/', include('apps.user.urls')),
]
