from rest_framework.exceptions import ValidationError

from .cleaner_serializer import create_user_and_find_proper_username
from users.models import Receptionist, Admin, HotelManager, Guest, Cleaner, Accountant


def create_model_for_every_kind_of_user(model_class_name: str, **validated_data):
    user_data = validated_data.pop('user')
    user = create_user_and_find_proper_username(**user_data)
    try:
        model_obj = eval(f'{model_class_name}.objects.create(user=user, **validated_data)')
    except Exception as e:
        raise ValidationError('creating the model failed ' + str(e))
    return model_obj
