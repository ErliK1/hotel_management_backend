from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from users.models import HotelManager, Admin

from users.serializers.hotel_manager_serializer import HotelManagerListSerializer, HotelManagerCreateSerializer
from users.views import get_user_type_from_retrieve

from users.permissions.hotel_manager_permissions import HotelManagerPermissions


class HotelManagerListCreateAPIView(ListCreateAPIView):
    queryset = HotelManager.objects.all()
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HotelManagerCreateSerializer
        else:
            return HotelManagerListSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return super(HotelManagerListCreateAPIView, self).create(request)

class HotelManagerRetrieveAPIView(RetrieveAPIView):
    queryset = HotelManager.objects.all()
    serializer_class = HotelManagerListSerializer
    permission_classes = [IsAuthenticated, HotelManagerPermissions]

    def get_object(self):
        if HotelManager.objects.filter(user=self.request.user).exists():
            return HotelManager.objects.get(user=self.request.user)
        elif Admin.objects.filter(user=self.request.user).exists():
            return HotelManager.objects.get(id=self.request.query_params.get('hotel_manager_id')) \
                if HotelManager.objects.filter(id=self.request.query_params.get('hotel_manager_id')).exists() else None

    def retrieve(self, request, *args, **kwargs):
        return get_user_type_from_retrieve(serializer_class=self.get_serializer_class(), type='Manager', obj=self.get_object())