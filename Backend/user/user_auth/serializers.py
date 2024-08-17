from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta(object):
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'password', 'email', 'username']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        if CustomUser.objects.filter(email=validated_data['email']).exists():
            raise ValidationError({'email': 'This email is already taken.'})

        if CustomUser.objects.filter(username=validated_data['username']).exists():
            raise ValidationError({'username': 'This username is already taken.'})

        user = CustomUser(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'email' in validated_data and validated_data['email'] != instance.email:
            if CustomUser.objects.filter(email=validated_data['email']).exists():
                raise ValidationError({'email': 'This email is already taken.'})
            instance.email = validated_data['email']

        if 'username' in validated_data and validated_data['username'] != instance.username:
            if CustomUser.objects.filter(username=validated_data['username']).exists():
                raise ValidationError({'username': 'This username is already taken.'})
            instance.username = validated_data['username']

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
