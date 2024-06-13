from rest_framework import serializers
from users.models import Cleaner, User
from .user_serializer import UserCreateSerializer, UserListSerializer
from abc import ABC

from datetime import datetime


def create_user_and_find_proper_username(**user_data):
    username: str = str(user_data.get('first_name')[0]) + '.' + user_data.get('last_name')
    counter: int = 1
    while User.objects.filter(username=username).exists():
        username = username + str(counter) if counter == 1 else username[0: -1] + str(counter)
        counter += 1
    user_data['username'] = username
    # if user_data.get('birthday'):
    #     user_data['birthday'] = datetime.strptime(user_data['birthday'], '%d/%m/%Y').date()
    user_data_obj: UserCreateSerializer = UserCreateSerializer(data=user_data)
    user_data_obj.is_valid(raise_exception=True)
    user = User.objects.create_user(**user_data)
    return user

class CleanerAbstractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cleaner
        fields = ('user', 'resume', 'notes', 'photo')
        abstract = True


class CleanerCreateSerializer(CleanerAbstractSerializer):
    user = UserCreateSerializer()

    class Meta(CleanerAbstractSerializer.Meta):
        pass

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = create_user_and_find_proper_username(**user_data)
        cleaner = Cleaner.objects.create(user=user, **validated_data)
        return cleaner


class CleanerListSerializer(CleanerAbstractSerializer):
    user = UserListSerializer(read_only=True)

    class Meta(CleanerAbstractSerializer.Meta):
        fields = CleanerAbstractSerializer.Meta.fields + ('id', )
