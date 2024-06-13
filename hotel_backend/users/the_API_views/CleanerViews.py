from django.db import transaction
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers.cleaner_serializer import CleanerListSerializer, CleanerCreateSerializer
from users.permissions.guest_permissions import GuestPermission
from users.permissions.admin_permisions import AdminPermission
from users.permissions.hotel_manager_permissions import HotelManagerPermissions
from users.permissions.cleaner_permissions import CleanerPermission

from users.models import Cleaner, Admin, HotelManager

from users.views import get_user_type_from_retrieve


class CleanerCreateListAPIView(ListCreateAPIView):
    queryset = Cleaner.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CleanerCreateSerializer
        else:
            return CleanerListSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return super(CleanerCreateListAPIView, self).create(request)


class CleanerRetrieveAPIView(RetrieveAPIView):
    queryset = Cleaner.objects.all()
    serializer_class = CleanerListSerializer
    permission_classes = [IsAuthenticated, CleanerPermission]

    def get_object(self):
        if Admin.objects.filter(user=self.request.user).exists() or HotelManager.objects.filter(
                user=self.request.user).exists():
            return Cleaner.objects.get(id=self.request.query_params.get('cleaner_id')) if Cleaner.objects.filter(
                id=self.request.query_params.get('cleaner_id')).exists() else None
        elif Cleaner.objects.filter(user=self.request.user).exists():
            return Cleaner.objects.get(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        return get_user_type_from_retrieve(serializer_class=self.get_serializer_class(), type='Cleaner', obj=self.get_object())

