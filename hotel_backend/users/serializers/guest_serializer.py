from rest_framework.serializers import ModelSerializer

from users.models import Guest

from .user_serializer import UserListSerializer, UserCreateSerializer
from .shared import create_model_for_every_kind_of_user


class GuestAbstractSerializer(ModelSerializer):
    class Meta:
        model = Guest
        fields = ('user', 'picture')
        abstract = True


class GuestCreateSerializer(GuestAbstractSerializer):
    user = UserCreateSerializer()

    class Meta(GuestAbstractSerializer.Meta):
        abstract = False

    def create(self, validated_data):
        return create_model_for_every_kind_of_user('Guest', **validated_data)


class GuestListSerializer(GuestAbstractSerializer):
    user = UserListSerializer(read_only=True)

    class Meta(GuestAbstractSerializer.Meta):
        abstract = False
        fields = ('id',) + GuestAbstractSerializer.Meta.fields
