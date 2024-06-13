from django.db import transaction
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework.response import Response

from users.serializers.guest_serializer import GuestListSerializer, GuestCreateSerializer, GuestAbstractSerializer

from users.models import Guest, Admin, HotelManager

from users.views import get_user_type_from_retrieve

from datetime import datetime


class GuestListCreateAPIView(ListCreateAPIView):
    queryset = Guest.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GuestCreateSerializer
        else:
            return GuestListSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs) -> Response:
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return super(GuestListCreateAPIView, self).create(request)


class GuestRetrieveAPIView(RetrieveAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestListSerializer

    def get_object(self) -> Guest:
        if Guest.objects.filter(user=self.request.user).exists():
            return Guest.objects.get(user=self.request.user)
        elif Admin.objects.filter(user=self.request.user).exists() or HotelManager.objects.filter(user=self.request.user).exists():
            return Guest.objects.get(id=self.request.query_params.get('guest_id')) if Guest.objects.filter(id=self.request.query_params.get('guest_id')).exists() else None

    def retrieve(self, request, *args, **kwargs):
        return get_user_type_from_retrieve(serializer_class=self.get_serializer_class(), type='Guest', obj=self.get_object())
