from django.db import transaction
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime

from rest_framework.views import APIView

from hotel_reservation.the_api_views.paginators import CustomPagination
from users.permissions.hotel_manager_permissions import HotelManagerPermissions
from .models import Feedback
from .serializers import FeedBackCreateSerializer, FeedBackListSerializer, FeedBackUpdateSerializer

from users.permissions.guest_permissions import GuestOnlyPermission, GuestPermission

from users.models import Guest


# Create your views here.


class FeedbackCreateAPIView(CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedBackCreateSerializer
    permission_classes = [IsAuthenticated, GuestOnlyPermission]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        guest_id = Guest.objects.get(user=request.user).id
        data_obj = {
            'guest': guest_id,
            **request.data
        }
        serializer_obj: FeedBackCreateSerializer = self.get_serializer(data=data_obj)
        serializer_obj.is_valid(raise_exception=True)
        serializer_obj.save()
        return Response(serializer_obj.data, status=status.HTTP_201_CREATED)


class FeedbackListAPIView(ListAPIView):
    serializer_class = FeedBackListSerializer
    permission_classes = [IsAuthenticated, GuestPermission]
    pagination_class = CustomPagination

    def get_queryset(self):
        guest = Guest.objects.get(user=self.request.user) if Guest.objects.filter(
            user=self.request.user).exists() else self.request.query_params.get('guest')
        s1 = list(filter(lambda x: 'date_time_created' in x, self.request.query_params.keys()))
        data = {}
        for k in s1:
            data[k] = datetime.strptime(self.request.query_params.get(k), '%d/%m/%Y') if self.request.query_params.get(
                k) else None

        filtered_data = {
            'viewed': False,
            'guest': guest,
            'stars': self.request.query_params.get('stars'),
            'stars__lte': self.request.query_params.get('stars__lte'),
            'stars__gte': self.request.query_params.get('stars__gte'),
            **data
        }
        final_filter_data = dict({k: v for k, v in filtered_data.items() if v is not None})
        return Feedback.objects.filter(**final_filter_data)


class FeedBackUpdateAPIVIew(UpdateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedBackUpdateSerializer
    permission_classes = [IsAuthenticated, GuestOnlyPermission]

    def get_object(self) -> Feedback:
        feedback_id = self.kwargs.get('feedback_id')
        return Feedback.objects.get(pk=feedback_id)

    def update(self, request, *args, **kwargs) -> Response:
        feedback_obj: Feedback = self.get_object()
        serializer_obj = self.get_serializer(feedback_obj, data=request.data)
        serializer_obj.is_valid(raise_exception=True)
        serializer_obj.save()
        return Response(serializer_obj.validated_data, status=status.HTTP_200_OK)


class FeedbackAverageAndTotal(APIView):
    permission_classes = [IsAuthenticated, HotelManagerPermissions]

    def get(self, request, *args, **kwargs):
        the_response = sum(Feedback.objects.all().values_list('stars', flat=True)) / len(
            Feedback.objects.all().values_list('stars', flat=True))
        return Response({'average': the_response,
                         'length': len(Feedback.objects.all().values_list('stars', flat=True))},
                        status=status.HTTP_200_OK)


class FeedbackViewedChangeAPIView(UpdateAPIView):
    queryset = Feedback.objects.all()
    permission_classes = [IsAuthenticated, HotelManagerPermissions]
    serializer_class = FeedBackListSerializer

    def update(self, request, *args, **kwargs):
        feedback_id = self.request.query_params.get('feedback_id')
        if not Feedback.objects.filter(id=feedback_id).exists():
            return Response({'message': 'Feedback not found'}, status=status.HTTP_404_NOT_FOUND)
        feedback_obj = Feedback.objects.get(id=feedback_id)
        feedback_obj.viewed = True
        feedback_obj.save()
        serializer = self.get_serializer(feedback_obj)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
