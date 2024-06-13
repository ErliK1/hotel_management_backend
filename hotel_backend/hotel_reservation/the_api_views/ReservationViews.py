from datetime import datetime
from functools import reduce

from django.http import HttpResponse
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import NotAcceptable, ValidationError, PermissionDenied

from users.permissions.guest_permissions import GuestPermission
from users.permissions.hotel_manager_permissions import HotelManagerPermissions
from users.permissions.receptionist_permissions import ReceptionistPermission
from .paginators import CustomPagination

from hotel_reservation.models import Reservation, Room, RoomReservation
from hotel_reservation.serializers.ReservationSerializers import ReservationCreateViaGuestUser, \
    ReservationCreateViaGuestInfo, ReservationListSerializer, ReservationPDFCreateAPIView, \
    ReservationReceiptViaGuestUser, ReservationReceiptViaGuestInfo, ReservationDateUpdateAPIVIew

from users.models import Guest, Receptionist

from hotel_reservation.views import calculate_the_total_cost_of_reservation, create_name_for_reservation

from .shared import check_if_room_is_free, check_if_specific_room_is_reserved
from ..pdfs.ReservationReceiptPDF import ReservationReceiptPDF


# def get_id_of_rooms_that_are_free(room_types: ):


class ReservationCreateAPIView(CreateAPIView):
    queryset = Reservation.objects.all()

    def get_serializer_class(self):
        if self.request.user.is_authenticated and Guest.objects.filter(user=self.request.user).exists():
            return ReservationCreateViaGuestUser
        if not self.request.user.is_authenticated or Receptionist.objects.filter(user=self.request.user).exists():
            return ReservationCreateViaGuestInfo

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        paid = True
        if not self.request.data.get('payment_intent_id'):
            paid = False
        if request.user.is_authenticated and Receptionist.objects.filter(user=request.user).exists():
            paid = request.data.get('paid')
        total_cost_of_reservation, payment_type = calculate_the_total_cost_of_reservation(request.data, request)

        # name_of_reservation = create_name_for_reservation(request.data) if request.user.is_authenticated and Guest.objects.filter(user=self.request.user).exists() else create_name_for_reservation(self.request.data, guest_account=False)
        # request.data['total_cost'] = total_cost_of_reservation
        # request.data['name'] = name_of_reservation
        the_data = {}
        for k, value in request.data.items():
            if k in ['start_date', 'end_date']:
                the_data[k] = datetime.strptime(value, '%d/%m/%Y').date()
            elif value:
                the_data[k] = value
        check_if_room_is_free(the_data.get('room_types'), the_data.get('start_date'), the_data.get('end_date'))

        # the_data = map(lambda k, v: {k: v[0]}, the_data)
        the_data['total_payment'] = total_cost_of_reservation
        the_data['payment_type'] = payment_type
        the_data['paid'] = paid
        serializer_obj = self.get_serializer(data=the_data)
        serializer_obj.is_valid(raise_exception=True)
        obj = serializer_obj.save()
        serializer_obj.validated_data['id'] = obj.id
        return Response(serializer_obj.validated_data, status=status.HTTP_201_CREATED)


class ReservationReceiptCreateAPIView(CreateAPIView):
    queryset = Reservation.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            if not Reservation.objects.filter(pk=request.data.get('reservation_id')).exists():
                return Response({'message': 'Reservation Not Found'}, status=status.HTTP_400_BAD_REQUEST)
            reservation_obj = Reservation.objects.get(pk=request.data.get('reservation_id'))
            serializer_obj = self.find_serializer_class(reservation_obj)(reservation_obj)
            response = HttpResponse(content_type='application/pdf')
            pdfMarker = ReservationReceiptPDF(data=serializer_obj.data)
            pdfMarker.main(response)
            return response
        except Exception as e:
            print(e)

    def find_serializer_class(self, reservation_obj: Reservation):
        if reservation_obj.guest_user:
            return ReservationReceiptViaGuestUser
        else:
            return ReservationReceiptViaGuestInfo


class ReservationListAPIVIew(ListAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationListSerializer
    permission_classes = [IsAuthenticated, ReceptionistPermission]

    def get_queryset(self):
        query_params = self.request.query_params
        reservation_queryset = Reservation.objects.exclude(end_date__lte=datetime.now().date(), cancelled=True)
        filter_diction = {
            # 'name__icontains': query_params.get('name', ''),
            'paid': query_params.get('paid'),
            'cancelled': query_params.get('cancelled'),
            'payment_type': query_params.get('payment_type')
        }
        filter_diction = {k: v for k, v in filter_diction.items() if v is not None}
        return reservation_queryset.filter(**filter_diction).order_by('-start_date')


class ReservationChangeDateAPIView(UpdateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationDateUpdateAPIVIew
    # permission_classes = [IsAuthenticated, GuestPermission, ReceptionistPermission]

    def get_permissions(self):
        if self.request.user.is_anonymous:
            raise PermissionDenied("Access Denied")
        elif Guest.objects.filter(user=self.request.user).exists():
            return [IsAuthenticated(), GuestPermission()]
        elif Receptionist.objects.filter(user=self.request.user).exists():
            return [IsAuthenticated(), ReceptionistPermission()]
        return super(ReservationChangeDateAPIView, self).get_permissions()

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        if not request.data.get('start_date') and not request.data.get('end_date'):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        reservation_obj: Reservation = self.get_object()
        start_date = datetime.strptime(request.data.get('start_date'), '%d/%m/%Y').date()
        end_date = datetime.strptime(request.data.get('end_date'), '%d/%m/%Y').date()
        rooms = reservation_obj.room_reservations.all().values_list('room', flat=True)
        n1 = reduce(lambda acc, y: acc or check_if_specific_room_is_reserved(y, start_date, end_date, reservation_obj.id) if
        isinstance(acc, bool) else check_if_specific_room_is_reserved(acc, start_date, end_date, reservation_obj.id) or
                                   check_if_specific_room_is_reserved(y, start_date, end_date, reservation_obj.id), rooms)
        if n1:
            return Response('Not all rooms are free in these days, please give us some other dates',
                            status=status.HTTP_400_BAD_REQUEST)
        data = {'start_date': start_date, 'end_date': end_date}
        days = (end_date - start_date).days
        the_new_total_cost = sum(reservation_obj.room_reservations.values_list('room__online_price',
                                                        flat=True)) * int(
            days) if reservation_obj.payment_type == 'online' else sum(
            reservation_obj.room_reservations.values_list('room__real_price', flat=True)) * int(days)
        reservation_obj.total_payment = the_new_total_cost
        serializer_obj = self.get_serializer(reservation_obj, data=data)
        serializer_obj.is_valid(raise_exception=True)
        serializer_obj.save()
        return Response(serializer_obj.data, status=status.HTTP_200_OK)


class ReservationChangePaidAPIView(UpdateAPIView):
    permission_classes = [IsAuthenticated, ReceptionistPermission]

    def update(self, request, *args, **kwargs):
        reservation_obj: Reservation = self.get_object()
        reservation_obj.paid = True
        reservation_obj.save()
        return Response(status=status.HTTP_200_OK)


class ReservationCancelAPIView(UpdateAPIView):
    # permission_classes = [IsAuthenticated, ReceptionistPermission, GuestPermission]

    def get_permissions(self):
        if self.request.user.is_anonymous:
            raise PermissionDenied("Access Denied")
        elif Guest.objects.filter(user=self.request.user).exists():
            return [IsAuthenticated(), GuestPermission()]
        elif Receptionist.objects.filter(user=self.request.user).exists():
            return [IsAuthenticated(), ReceptionistPermission()]
        return super(ReservationCancelAPIView, self).get_permissions()


    def update(self, request, *args, **kwargs):
        reservation_obj: Reservation = self.get_object()
        reservation_obj.cancelled = True
        reservation_obj.save()
        return Response(status=status.HTTP_200_OK)


class ReservationDeleteRoomAPIView(UpdateAPIView):
    # permission_classes = [IsAuthenticated, ReceptionistPermission, GuestPermission]
    serializer_class = ReservationListSerializer

    def get_permissions(self):
        if self.request.user.is_anonymous:
            raise PermissionDenied("Access Denied")
        elif Guest.objects.filter(user=self.request.user).exists():
            return [IsAuthenticated(), GuestPermission()]
        elif Receptionist.objects.filter(user=self.request.user).exists():
            return [IsAuthenticated(), ReceptionistPermission()]
        return super(ReservationDeleteRoomAPIView, self).get_permissions()

    def get_object(self):
        if Reservation.objects.filter(id=self.kwargs.get('reservation_id')).exists():
            return Reservation.objects.get(id=self.kwargs.get('reservation_id'))
        raise ValidationError("Not Found")
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            if not Room.objects.filter(id=kwargs['room_id']).exists() and not Reservation.objects.filter(
                    room_id=kwargs['reservation_id']).exists():
                return Response({'message': "Please provide id of room and reservation"},
                                status=status.HTTP_404_NOT_FOUND)
            reservation_obj = Reservation.objects.get(id=kwargs['reservation_id'])
            room_obj = Room.objects.get(id=kwargs['room_id'])
            room_reservation: RoomReservation = room_obj.room_reservations.filter(room_id=room_obj.id,
                                                                                  reservation_id=reservation_obj.id).first()
            room_reservation.delete()
            rooms_left = RoomReservation.objects.filter(reservation_id=reservation_obj.id)
            number_of_days = (reservation_obj.end_date - reservation_obj.start_date).days
            the_new_total_cost = sum(rooms_left.values_list('room__online_price',
                                                            flat=True)) * int(number_of_days) if reservation_obj.payment_type == 'online' else sum(
                rooms_left.values_list('room__real_price', flat=True)) * int(number_of_days)
            reservation_obj.total_payment = the_new_total_cost
            reservation_obj.save()
            serializer_obj = self.get_serializer(reservation_obj)
            return Response(serializer_obj.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
