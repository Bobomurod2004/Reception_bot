from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'telegram_id',
            'username',
            'first_name',
            'last_name',
            'is_blocked',
            'language',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'telegram_id',
            'username',
            'first_name',
            'last_name',
            'language',
            'created_at',
            'updated_at',
        ]
        extra_kwargs = {
            'telegram_id': {'required': True},
        }
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        return User.objects.create(**validated_data)
