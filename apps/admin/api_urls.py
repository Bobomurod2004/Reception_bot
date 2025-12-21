from django.urls import path
from .views import (
    AdminViewSet,
    CategoryViewSet,
    AdminCategoryViewSet,
    AdminActivityViewSet,
)

urlpatterns = [
    path('admins/', AdminViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('admins/<int:pk>/', AdminViewSet.as_view({
        'get': 'retrieve', 'put': 'update',
        'patch': 'partial_update', 'delete': 'destroy'
    })),
    path('categories/', CategoryViewSet.as_view(
         {'get': 'list', 'post': 'create'})),
    path('categories/<int:pk>/', CategoryViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch':
        'partial_update', 'delete': 'destroy'
    })),
    path('admin-categories/', AdminCategoryViewSet.as_view(
         {'get': 'list', 'post': 'create'})),
    path('admin-categories/<int:pk>/', AdminCategoryViewSet.as_view({
        'get': 'retrieve', 'put': 'update',
        'patch': 'partial_update', 'delete': 'destroy'
    })),
    path('admin-activities/', AdminActivityViewSet.as_view(
         {'get': 'list', 'post': 'create'})),
    path('admin-activities/<int:pk>/', AdminActivityViewSet.as_view({
        'get': 'retrieve', 'put': 'update',
        'patch': 'partial_update', 'delete': 'destroy'
    })),
]
