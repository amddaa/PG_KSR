from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['id', 'username', 'password', 'email']

    # def validate(self, value):
    #     if User.objects.filter(username=value).exists() or User.objects.filter(email=value).exists():
    #         raise serializers.ValidationError("Username or email already exists.")
    #     return value
