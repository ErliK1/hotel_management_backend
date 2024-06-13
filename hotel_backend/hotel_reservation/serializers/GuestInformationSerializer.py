from rest_framework import serializers
from hotel_reservation.models import GuestInformation


class GuestAbstractInformation(serializers.ModelSerializer):
    class Meta:
        model = GuestInformation
        fields = ('email', 'first_name', 'fathers_name', 'last_name', 'birthday', 'birthplace', 'personal_number',
                  'gender', 'phone_number')


class GuestInformationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestInformation
        fields = ('email', 'first_name', 'fathers_name', 'last_name', 'birthday', 'birthplace', 'personal_number',
                  'gender', 'phone_number')
