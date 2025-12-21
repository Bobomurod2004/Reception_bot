from rest_framework import serializers
from .models import Ticket, Message


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id',
            'user',
            'title',
            'category',
            'status',
            'description',
            'priority',
            'assigned_admin',
            'is_read',
            'read_at',
            'close_at',
            'closed_by',
            'ticket_number',
            'close_reason',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'ticket_number']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id',
            'ticket',
            'sender_user',
            'sender_admin',
            'content_type',
            'content',
            'file',
            'timestamp',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['timestamp', 'created_at', 'updated_at']
