from rest_framework.serializers import ModelSerializer

from .cleaner_serializer import create_user_and_find_proper_username
from .user_serializer import UserCreateSerializer, UserListSerializer

from users.models import Receptionist, User

from .shared import create_model_for_every_kind_of_user


class ReceptionistAbstractSerializer(ModelSerializer):
    class Meta:
        model = Receptionist
        fields = ('user', 'resume', 'notes', 'photo')
        abstract = True


class ReceptionistCreateSerializer(ReceptionistAbstractSerializer):
    user = UserCreateSerializer()

    class Meta(ReceptionistAbstractSerializer.Meta):
        pass

    def create(self, validated_data):
        receptionist = create_model_for_every_kind_of_user('Receptionist', **validated_data)
        return receptionist



class ReceptionistListSerializer(ReceptionistAbstractSerializer):
    user = UserListSerializer(read_only=True)

    class Meta(ReceptionistAbstractSerializer.Meta):
        fields = ('id',) + ReceptionistAbstractSerializer.Meta.fields
