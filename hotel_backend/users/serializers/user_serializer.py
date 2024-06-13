from rest_framework import serializers
from users.models import User

from abc import ABC


class UserAbstractSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'fathers_name', 'last_name',
                  'email', 'birthday', 'birthplace',
                  'personal_number', 'gender', 'phone_number')
        abstract = True


class UserCreateSerializer(UserAbstractSerializer):
    class Meta(UserAbstractSerializer.Meta):
        fields = UserAbstractSerializer.Meta.fields + ('password', )


class UserListSerializer(UserAbstractSerializer):
    class Meta(UserAbstractSerializer.Meta):
        fields = ('id',) + UserAbstractSerializer.Meta.fields


