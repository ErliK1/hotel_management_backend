from django.db import transaction

from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from users.models import Receptionist, HotelManager, Admin

from users.serializers.receptionist_serializer import ReceptionistListSerializer, ReceptionistCreateSerializer
from users.views import get_user_type_from_retrieve

from users.permissions.receptionist_permissions import ReceptionistPermission

class ReceptionistListCreateAPIView(ListCreateAPIView):
    queryset = Receptionist.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReceptionistCreateSerializer
        else:
            return ReceptionistListSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return super(ReceptionistListCreateAPIView, self).create(request)

class ReceptionistRetrieveAPIView(RetrieveAPIView):
    queryset = Receptionist.objects.all()
    serializer_class = ReceptionistListSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        if Receptionist.objects.filter(user=self.request.user).exists():
            return Receptionist.objects.get(user=self.request.user)
        elif HotelManager.objects.filter(user=self.request.user).exists() or Admin.objects.filter(user=self.request.user).exists():
            if Receptionist.objects.filter(id=self.request.query_params.get('receptionist_id')).exists():
                return Receptionist.objects.get(id=self.request.query_params.get('receptionist_id'))

    def retrieve(self, request, *args, **kwargs):
        return get_user_type_from_retrieve(serializer_class=self.get_serializer_class(), type='Receptionist', obj=self.get_object())