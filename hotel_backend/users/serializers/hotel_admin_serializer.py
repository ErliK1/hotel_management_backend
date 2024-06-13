from rest_framework.serializers import ModelSerializer
from users.models import Admin, User

from .user_serializer import UserCreateSerializer, UserListSerializer
from .cleaner_serializer import create_user_and_find_proper_username


class AdminAbstractSerializer(ModelSerializer):
    class Meta:
        model = Admin
        fields = ('user',)
        abstract = True


class AdminCreateSerializer(AdminAbstractSerializer):
    user = UserCreateSerializer()

    class Meta(AdminAbstractSerializer.Meta):
        abstract = False

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user: User = create_user_and_find_proper_username(**user_data)
        admin: Admin = Admin.objects.create(user=user, **validated_data)
        return admin


class AdminListSerializer(AdminCreateSerializer):
    user = UserListSerializer(read_only=True)

    class Meta(AdminCreateSerializer.Meta):
        abstract = False
        fields = ('id',) + AdminAbstractSerializer.Meta.fields
