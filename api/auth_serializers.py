"""
User serializers for authentication
"""
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .models import User


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Custom serializer for user creation
    """
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'username', 'email', 'password')


class CustomUserSerializer(UserSerializer):
    """
    Custom serializer for user details
    """
    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
