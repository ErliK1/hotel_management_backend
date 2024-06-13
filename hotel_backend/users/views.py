from django.db import transaction
from django.shortcuts import render
from django.conf import settings

from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed, NotFound

from .serializers import cleaner_serializer, guest_serializer, hotel_admin_serializer, hotel_manager_serializer, \
    receptionist_serializer, accountant_serializer
from .models import Cleaner, Guest, Admin, HotelManager, Accountant, Receptionist


# Create your the_API_views here.

class CleanerCreateView(CreateAPIView):
    queryset = Cleaner.objects.all()
    serializer_class = cleaner_serializer.CleanerCreateSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Createde!'}, status=status.HTTP_201_CREATED)


class LogInView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, ]
    user_type = ''

    def get_serializer_class(self):
        if Guest.objects.filter(user=self.request.user).exists():
            return guest_serializer.GuestListSerializer
        elif Admin.objects.filter(user=self.request.user).exists():
            return hotel_admin_serializer.AdminListSerializer
        elif HotelManager.objects.filter(user=self.request.user).exists():
            return hotel_manager_serializer.HotelManagerListSerializer
        elif Cleaner.objects.filter(user=self.request.user).exists():
            return cleaner_serializer.CleanerListSerializer
        elif Receptionist.objects.filter(user=self.request.user).exists():
            return receptionist_serializer.ReceptionistListSerializer
        elif Accountant.objects.filter(user=self.request.user).exists():
            return accountant_serializer.AccountantListSerializer
        else:
            raise AuthenticationFailed('User not Found')

    def get_object(self):
        if Guest.objects.filter(user=self.request.user).exists():
            self.user_type = 'Guest'
            return Guest.objects.get(user=self.request.user)
        elif Admin.objects.filter(user=self.request.user).exists():
            self.user_type = 'Admin'
            return Admin.objects.get(user=self.request.user)
        elif HotelManager.objects.filter(user=self.request.user).exists():
            self.user_type = 'Manager'
            return HotelManager.objects.get(user=self.request.user)
        elif Receptionist.objects.filter(user=self.request.user).exists():
            self.user_type = 'Receptionist'
            return Receptionist.objects.get(user=self.request.user)
        elif Cleaner.objects.filter(user=self.request.user).exists():
            self.user_type = 'Cleaner'
            return Cleaner.objects.get(user=self.request.user)
        elif Accountant.objects.filter(user=self.request.user).exists():
            self.user_type = 'Accountant'
            return Accountant.objects.get(user=self.request.user)
        else:
            raise NotFound('Object Not Found')

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        return get_user_type_from_retrieve(serializer_class=self.get_serializer_class(), obj=obj, type=self.user_type)


def get_user_type_from_retrieve(serializer_class, type, obj):
    if not obj:
        return Response({'message': 'Error, Please write the user you want to get'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = serializer_class(obj)
    data = serializer.data
    data['type'] = type
    return Response(data, status=status.HTTP_200_OK)


def create_employee_from_view(serializer_class, request, *args, **kwargs):
    serializer = serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    serializer.validated_data[
        'photo'] = settings.MEDIA_URL + '/' + 'employee/' + 'images/' + serializer.validated_data.get('photo').name
    serializer.validated_data[
        'resume'] = settings.MEDIA_URL + '/' + 'employee/' + 'documents/' + serializer.validated_data.get(
        'resume').name
    serializer.validated_data['user'].pop('password')
    return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
