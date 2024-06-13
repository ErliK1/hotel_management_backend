from rest_framework.serializers import ModelSerializer

from .user_serializer import UserCreateSerializer, UserListSerializer
from .shared import create_model_for_every_kind_of_user

from users.models import HotelManager


class HotelManagerAbstractSerializer(ModelSerializer):
    class Meta:
        model = HotelManager
        fields = ('user', 'resume', 'notes', 'photo')
        abstract = True


class HotelManagerCreateSerializer(HotelManagerAbstractSerializer):
    user = UserCreateSerializer()

    class Meta(HotelManagerAbstractSerializer.Meta):
        abstract = False

    def create(self, validated_data):
        return create_model_for_every_kind_of_user('HotelManager', **validated_data)


class HotelManagerListSerializer(HotelManagerAbstractSerializer):
    user = UserListSerializer(read_only=True)

    class Meta(HotelManagerAbstractSerializer.Meta):
        abstract = False
        fields = ('id',) + HotelManagerAbstractSerializer.Meta.fields
