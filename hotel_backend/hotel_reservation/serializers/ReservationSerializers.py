from datetime import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from hotel_reservation.models import Reservation, GuestInformation, Room, RoomReservation, RoomType

from hotel_reservation.serializers.GuestInformationSerializer import GuestInformationCreateSerializer
from users.serializers.guest_serializer import GuestListSerializer
from .RoomSerializer import RoomListSerializer

from .validators import date_today_serializer

from hotel_reservation.the_api_views.shared import get_the_room_for_diferent_days

from functools import reduce


def find_room_ids_from_room_types(room_types: [], start_date, end_date):
    list_of_rooms_that_will_be_reserved = []
    for element in room_types:
        room_all_query_set = Room.objects.filter(room_type__id=element.get('id')).values_list('id',
                                                                                                       flat=True).order_by(
            'id')
        room_for_given_dates = get_the_room_for_diferent_days(start_date=start_date, end_date=end_date,
                                                              key=element.get('id')).values_list('id',
                                                                                                   flat=True).order_by(
            'id')
        rooms_available_for_given_date = sorted(list(filter(lambda x: x not in room_for_given_dates, room_all_query_set)))
        if len(rooms_available_for_given_date) < element.get('count'):
            raise ValidationError("Not enough Rooms")
        rooms_to_be_added = [rooms_available_for_given_date[i] for i in range(int(element.get('count')))]
        list_of_rooms_that_will_be_reserved.extend(rooms_to_be_added)
        # for i in room_all_query_set:
        #     if i not in room_for_given_dates and count < element.get('count'):
        #         list_of_rooms_that_will_be_reserved.append(i)
    return list_of_rooms_that_will_be_reserved


class ReservationAbstractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ('name', 'start_date', 'end_date')


class ReservationFilterFromRoomSerializer(ReservationAbstractSerializer):
    class Meta(ReservationAbstractSerializer.Meta):
        model = Reservation
        fields = ('id',) + ReservationAbstractSerializer.Meta.fields


class ReservationFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ('paid', 'start_date', 'end_date', 'cancelled', 'payment_type')
        extra_kwargs = {'paid': {'allow_blank': True},
                        'start_date': {'allow_blank': True},
                        'end_date': {'allow_blank': True},
                        'cancelled': {'allow_blank': True},
                        'payment_type': {'allow_blank': True},
                        }

    def validate(self, attrs):
        for key, value in attrs.items():
            if not value:
                attrs.pop(key)
        return attrs

class RoomTypeForReservationCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    count = serializers.IntegerField()


class ReservationCreateViaGuestUser(ReservationAbstractSerializer):
    room_types = RoomTypeForReservationCreateSerializer(many=True)
    class Meta(ReservationAbstractSerializer.Meta):
        model = Reservation
        fields = ('guest_user', 'payment_type', 'payment_intent_id',
                  'total_payment', 'paid', 'room_types') + ReservationAbstractSerializer.Meta.fields

    def validate(self, attrs):
        return validate_start_and_end_date(attrs)

    def create(self, validated_data):
        room_types = validated_data.pop('room_types')
        reservation_obj = Reservation.objects.create(**validated_data)
        room_ids = find_room_ids_from_room_types(room_types, reservation_obj.start_date, reservation_obj.end_date)
        # RoomReservation.objects.create(room_id=int(room_id), reservation=reservation_obj)
        for room_id in room_ids:
            RoomReservation.objects.create(room_id=room_id, reservation=reservation_obj)
        return reservation_obj


class ReservationPDFCreateAPIView(ReservationAbstractSerializer):
    guest_user = GuestListSerializer(read_only=True)

    class Meta(ReservationAbstractSerializer.Meta):
        model = Reservation
        fields = ('guest_user', 'payment_type', 'payment_intent_id',
                  'total_payment') + ReservationAbstractSerializer.Meta.fields




class ReservationCreateViaGuestInfo(ReservationAbstractSerializer):
    guest_information = GuestInformationCreateSerializer()
    room_types = RoomTypeForReservationCreateSerializer(many=True)

    class Meta(ReservationAbstractSerializer.Meta):
        model = Reservation
        fields = ('guest_information', 'payment_type', 'payment_intent_id', 'total_payment', 'paid', 'room_types'
                  ) + ReservationAbstractSerializer.Meta.fields

    def validate(self, attrs):
        return validate_start_and_end_date(attrs)

    def create(self, validated_data):
        guest_information = validated_data.pop('guest_information')
        guest_information_obj = GuestInformation.objects.create(**guest_information)
        room_types = validated_data.pop('room_types')
        reservation_obj = Reservation.objects.create(**validated_data, guest_information=guest_information_obj)
        room_ids = find_room_ids_from_room_types(room_types, reservation_obj.start_date, reservation_obj.end_date)
        # RoomReservation.objects.create(room_id=int(room_id), reservation=reservation_obj)
        for room_id in room_ids:
            RoomReservation.objects.create(room_id=room_id, reservation=reservation_obj)
        return reservation_obj


class RoomReservationListSerializer(serializers.ModelSerializer):
    room = RoomListSerializer(read_only=True)

    class Meta:
        model = RoomReservation
        fields = ('room', )


class ReservationListSerializer(ReservationAbstractSerializer):
    reservation_cost = serializers.SerializerMethodField()
    person_info = serializers.SerializerMethodField()
    room_reservations = RoomReservationListSerializer(many=True, read_only=True)

    class Meta(ReservationAbstractSerializer.Meta):
        fields = ReservationAbstractSerializer.Meta.fields + ('applying_date', 'room_reservations',
                                                              'reservation_cost', 'person_info', 'id')

    def get_person_info(self, obj: Reservation):
        if obj.guest_information:
            return obj.guest_information.email
        return obj.guest_user.user.email

    def get_reservation_cost(self, obj: Reservation):
        start_date = obj.start_date
        end_date = obj.end_date
        days = (end_date - start_date).days
        if obj.payment_type == 'online':
            return sum(obj.room_reservations.all().values_list('room__online_price', flat=True)) * days
        elif obj.payment_type == 'reception':
            return sum(obj.room_reservations.all().values_list('room__real_price', flat=True)) * days


class ReservationReceiptViaGuestInfo(ReservationCreateViaGuestInfo):
    real_total_payment = serializers.SerializerMethodField()

    class Meta(ReservationCreateViaGuestInfo.Meta):
        fields = ('id', 'real_total_payment') + ReservationCreateViaGuestInfo.Meta.fields

    def get_real_total_payment(self, obj: Reservation):
        room_reservations = obj.room_reservations.all()
        total_payment = 0
        for room_reservation in room_reservations:
            room = room_reservation.room
            total_payment += room.online_price if obj.payment_type == 'online' else room.real_price
        return total_payment


class ReservationReceiptViaGuestUser(ReservationCreateViaGuestUser):
    room_numbers = serializers.SerializerMethodField()

    class Meta(ReservationCreateViaGuestUser.Meta):
        fields = ('id', 'room_numbers') + ReservationCreateViaGuestUser.Meta.fields

    def get_room_numbers(self, obj: Reservation):
        room_reservation = obj.room_reservations.all()
        output_string = ''
        for room_reservation in room_reservation:
            output_string += room_reservation.room.room_unique_number + ' ' + room_reservation.room.room_type.type_name + '<br/>'
        return output_string


class ReservationDateUpdateAPIVIew(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ('start_date', 'end_date')

    def validate(self, attrs):
        return validate_start_and_end_date(attrs)

    def update(self, instance: Reservation, validated_data):
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.save()
        return instance

def validate_start_and_end_date(attrs):
    if attrs.get('start_date') >= attrs.get('end_date'):
        raise ValidationError("Start date must be smaller than end date")
    if attrs.get('start_date') < datetime.now().date():
        raise ValidationError("Start date must be in the future")
    if attrs.get('end_date') < datetime.now().date():
        raise ValidationError("End date must be in the future")
    return attrs