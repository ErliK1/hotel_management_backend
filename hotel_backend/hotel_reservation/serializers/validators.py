from rest_framework.serializers import ValidationError
from datetime import date

def room_name_validator(value):
    if not value:
        raise ValidationError('room_name is required')
    return value


def size_room_type_validator(value):
    if not value:
        raise ValidationError('Size should not be empty!')
    return value

def date_today_serializer(value):
    if value and value < date.today():
        raise ValidationError('Date is in the past! Need a date in the future!')
    return value