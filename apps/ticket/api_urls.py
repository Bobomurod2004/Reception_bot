# from rest_framework.routers import DefaultRouter

from django.urls import path
from .views import TicketViewSet, MessageViewSet

# router = DefaultRouter()
# router.register(r'tickets', TicketViewSet)
# router.register(r'messages', MessageViewSet)

# urlpatterns = router.urls

urlpatterns = [
    path('tickets/', TicketViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='ticket-list'),
    path('tickets/<int:pk>/', TicketViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='ticket-detail'),
    path('tickets/<int:pk>/assign-admin/', TicketViewSet.as_view({
        'post': 'assign_admin'
    }), name='ticket-assign-admin'),
    path('tickets/<int:pk>/close/', TicketViewSet.as_view({
        'post': 'close_ticket'
    }), name='ticket-close'),
    path('tickets/my-tickets/', TicketViewSet.as_view({
        'get': 'my_tickets'
    }), name='admin-tickets'),
    path('tickets/user-tickets/', TicketViewSet.as_view({
        'get': 'user_tickets'
    }), name='user-tickets'),
    path('tickets/close_expired/', TicketViewSet.as_view({
        'post': 'close_expired'
    }), name='ticket-close-expired'),
    path('messages/', MessageViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='message-list'),
    path('messages/<int:pk>/', MessageViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='message-detail'),
]
