from django.db import transaction
from django.http import QueryDict, Http404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from hotel_reservation.models import Reservation, RoomReservation, Room, RoomType
from hotel_reservation.serializers.RoomSerializer import RoomListSerializer, RoomTypeCustomSerializer, \
    RoomCreateSerializer, RoomtypeListForScrollSerializer, RoomTypeCreateSerializer, RoomTypeUpdatePriceSerializer
from users.permissions.hotel_manager_permissions import HotelManagerPermissions
from .paginators import CustomPagination

from .shared import get_the_room_for_diferent_days, parse_to_date_time_dd_mm_yy_version

from datetime import datetime, timedelta

import json

START_DATE_ROOM_KEY: str = 'room_reservations__reservation__start_date'
END_DATE_ROOM_KEY: str = 'room_reservations__reservation__end_date'


class RoomListAPIView(ListAPIView):
    '''
    For the guests and all. They can check the type of rooms that are free in the dyas wanted
    '''
    queryset = Room.objects.all()
    serializer_class = RoomTypeCustomSerializer
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        if self.request.query_params.get('start_date') and self.request.query_params.get('end_date'):
            start_date = datetime.strptime(self.request.query_params.get('start_date'), '%d/%m/%Y').date()
            end_date = (datetime.strptime(self.request.query_params.get('end_date'), '%d/%m/%Y')).date()
            room_query_set = Room.objects.exclude(pk__in=get_the_room_for_diferent_days(start_date, end_date,
                                                                                        self.request.query_params.get(
                                                                                            "room_type")).values_list(
                'id', flat=True))
            room_query_set.order_by('room_type')
        else:
            room_query_set = Room.objects.all().order_by('room_type')
        data_1 = []
        r1 = list(room_query_set)
        count = 0
        for i, elemenet in enumerate(room_query_set):
            if len(list(filter(lambda x: x.get('room_type') == elemenet.room_type, data_1))) == 0:
                data_1.append({
                    'room_type': elemenet.room_type,
                    'room_count': 0,
                })
            data_1[-1]['room_count'] += 1
        serializer_obj: RoomTypeCustomSerializer = self.get_serializer(data_1, many=True) if len(
            data_1) else self.get_serializer(data_1)
        return Response(serializer_obj.data, status=status.HTTP_200_OK)
        #
        # for key, value in filter_dictionary.items():
        #     for k, v in value.items():
        #         if v is not None:
        #             value[k] = v
        # r1 = Room.objects.all()
        # return r1


class RoomAdminListAPIView(ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomListSerializer
    permission_classes = [IsAuthenticated, HotelManagerPermissions]
    # pagination_class = CustomPagination
    '''
    Rooms for the admins or managers
    '''

    def get_queryset(self):
        return Room.objects.all()

    def get_queryset_for_given_reservation_dates(self, start_date, end_date):
        return get_the_room_for_diferent_days(start_date, end_date, self.request.query_params.get('room_type'))

    def get_queryset_except_given_reservation_dates(self, start_date, end_date):
        return Room.objects.exclude(pk__in=get_the_room_for_diferent_days(start_date, end_date,
                                                                          self.request.query_params.get(
                                                                              'room_type')).values_list('id',
                                                                                                        flat=True))

    def filter_the_queryset(self, the_query_set):
        filter_dict = {
            'room_type__id': self.request.query_params.get('room_type'),
            'room_type__size': self.request.query_params.get('size'),
            'room_type__price': self.request.query_params.get('price'),
            'clean': self.request.query_params.get('clean')
        }
        filter_dict = {k: v for k, v in filter_dict.items() if v is not None}
        return the_query_set.filter(**filter_dict)


class FinanceProfitsListAPIView(ListAPIView):
    pass


class RoomCreateAPIView(CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomCreateSerializer
    permission_classes = [IsAuthenticated, HotelManagerPermissions]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        room_type_id = self.request.data.get('room_type')
        if not RoomType.objects.filter(pk=room_type_id).exists():
            return Response({'message': 'Room Failed'}, status=status.HTTP_400_BAD_REQUEST)
        if Room.objects.filter(room_unique_number=self.request.data.get('room_unique_number')).exists():
            return Response({'message': 'Rooom Already Exists'}, status=status.HTTP_400_BAD_REQUEST)
        room_type = RoomType.objects.get(id=room_type_id)
        data = {
            'online_price': room_type.online_price,
            'real_price': room_type.real_price,
            'size': room_type.size,
            **request.data
        }
        serializer: RoomCreateSerializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        room_type.total_count += 1
        room_type.save()
        serializer.data['id'] = room_type.id
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RoomTypeListForScrollerAPIView(ListAPIView):
    queryset = RoomType.objects.all()
    serializer_class = RoomtypeListForScrollSerializer
    permission_classes = [IsAuthenticated]


class RoomTypeCreateAPIView(CreateAPIView):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeCreateSerializer
    permission_classes = [IsAuthenticated, HotelManagerPermissions]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if not request.data.get('price'):
            return Response({'message': "Please provide the price of room type"}, status=status.HTTP_400_BAD_REQUEST)
        online_price = self.find_online_price(request.data)
        real_price = int(request.data.get('price'))
        total_count = 0
        data = {
            'online_price': online_price,
            'real_price': real_price,
            'total_count': total_count,
            **request.data
        }
        data.pop('price')
        serializer: RoomTypeCreateSerializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def find_online_price(self, the_data):
        return int(the_data.get('price')) + 2

    def parse_to_dictionary(self):
        data = {}
        d1 = dict(self.request.data)
        for k, v in d1.items():
            data[k] = v[0]
        return data

class RoomTypeChangePriceAPIView(UpdateAPIView):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeUpdatePriceSerializer
    permission_classes = [IsAuthenticated, HotelManagerPermissions]

    def get_object(self):
        if not RoomType.objects.filter(id=self.kwargs.get('roomtype_id')).exists():
            raise Http404("Object Not Found")
        return RoomType.objects.get(id=self.kwargs.get('roomtype_id'))

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        real_price = self.request.data.get('price')
        if not real_price:
            return Response({'detail': 'Please Provide the Price'}, status=status.HTTP_400_BAD_REQUEST)
        data = {
            'real_price': float(real_price),
            'online_price': float(real_price) + 2
        }
        serializer_obj = self.get_serializer(self.get_object(), data=data)
        serializer_obj.is_valid(raise_exception=True)
        serializer_obj.save()
        return Response(serializer_obj.validated_data, status=status.HTTP_200_OK)
