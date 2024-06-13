from django.db import transaction

from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from users.models import Admin

from users.serializers.hotel_admin_serializer import AdminCreateSerializer, AdminListSerializer
from users.views import get_user_type_from_retrieve
from users.permissions.admin_permisions import AdminPermission

class HotelAdminListCreateAPIView(ListCreateAPIView):
    queryset = Admin.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminCreateSerializer
        else:
            return AdminListSerializer

    def get_queryset(self):
        query_params = self.request.query_params
        return Admin.objects.all()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return super(HotelAdminListCreateAPIView, self).create(request)


class HotelAdminRetrieveAPIView(RetrieveAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminListSerializer
    permission_classes = [IsAuthenticated, AdminPermission]

    def get_object(self):
        if Admin.objects.filter(user=self.request.user).exists():
            return Admin.objects.get(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        return get_user_type_from_retrieve(serializer_class=self.get_serializer_class(), type='Admin', obj=self.get_object())
