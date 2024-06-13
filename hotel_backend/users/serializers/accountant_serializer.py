from rest_framework.serializers import ModelSerializer

from users.models import Accountant

from .user_serializer import UserListSerializer, UserCreateSerializer
from .shared import create_model_for_every_kind_of_user


class AccountantAbstractSerializer(ModelSerializer):
    class Meta:
        model = Accountant
        fields = ('user', 'resume', 'notes', 'photo')
        abstract = True


class AccountantCreateSerializer(AccountantAbstractSerializer):
    user = UserCreateSerializer()

    class Meta(AccountantAbstractSerializer.Meta):
        abstract = False

    def create(self, validated_data):
        return create_model_for_every_kind_of_user('Accountant', **validated_data)


class AccountantListSerializer(AccountantAbstractSerializer):
    user = UserListSerializer(read_only=True)

    class Meta(AccountantAbstractSerializer.Meta):
        abstract = False
        fields = ('id',) + AccountantAbstractSerializer.Meta.fields
