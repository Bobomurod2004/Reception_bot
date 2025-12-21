from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from .models import User
from apps.user.serializer import UserSerializer, CreateUserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        telegram_id = self.request.query_params.get('telegram_id')
        if telegram_id:
            queryset = queryset.filter(telegram_id=telegram_id)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer

    def perform_create(self, serializer):
        serializer.save()
        return serializer.instance

    def perform_update(self, serializer):
        serializer.save()
        return serializer.instance

    def perform_destroy(self, instance):
        instance.delete()
        return instance

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
