from django.shortcuts import render
import stripe
from datetime import datetime
from .models import Room

from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError

from users.models import Guest, Receptionist

from hotel_reservation.serializers.ReservationSerializers import find_room_ids_from_room_types

# from hotel_reservation.the_api_views.ReservationViews import check_if_room_is_free
from hotel_reservation.the_api_views.shared import check_if_room_is_free

stripe.api_key = settings.STRIPE_SECRET_KEY


# Create your the_api_views here.



def calculate_the_total_cost_of_reservation(data, request: Request):
    if not data.get('start_date') or not data.get('end_date') or not request.data.get('room_types'):
        raise ValidationError('Please Enter Start and ENd Date or The room you want to order')
    start_date = datetime.strptime(data.get('start_date'), '%d/%m/%Y')
    end_date = datetime.strptime(data.get('end_date'), '%d/%m/%Y')
    difference_days = end_date - start_date
    room_ids: [] = find_room_ids_from_room_types(room_types=request.data.get('room_types'), start_date=start_date, end_date=end_date)
    room_queryset = Room.objects.filter(pk__in=room_ids).order_by('id')
    if ((not request.user.is_authenticated or Guest.objects.filter(user=request.user).exists())
            and data.get('payment_intent_id')):
        total_price, payment_type = sum(room_queryset.values_list('online_price', flat=True)) * difference_days.days, 'online'
    elif (not request.user.is_authenticated or Guest.objects.filter(user=request.user) and not data.get('payment_intent_id')):
        total_price, payment_type = sum(
            room_queryset.values_list('real_price', flat=True)) * difference_days.days, 'reception'
    elif Receptionist.objects.filter(user=request.user).exists():
        total_price, payment_type = sum(room_queryset.values_list('real_price', flat=True)) * difference_days.days, 'reception'
    else:
        raise ValueError('No total_price_found')
    return total_price, payment_type


def create_name_for_reservation(data, guest_account=True):
    if guest_account:
        guest = Guest.objects.get(id=data.get('guest_id'))
        name_for_reservation = guest.user.first_name + ' ' + guest.user.last_name + str(datetime.now())
    else:
        name_for_reservation = data.get('guest_info.first_name') + ' ' + data.get(
            'guest_info.last_name') + str(datetime.now())

    return name_for_reservation


class PaymentIntentAPIView(APIView):

    def post(self, request):
        try:
            total_amount = calculate_the_total_cost_of_reservation(self.request.data, self.request)
            check_if_room_is_free(room_types=self.request.get('room_types'), start_date=self.request.get('start_date'),
                                  end_date=self.request.get('end_date'))
            payment_intent = stripe.PaymentIntent.create(
                amount=total_amount,
                currency='eur',
                payment_method_types=['card']
            )
            return Response({
                'id': payment_intent.id,
                'client_secret': payment_intent.client_secret
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
