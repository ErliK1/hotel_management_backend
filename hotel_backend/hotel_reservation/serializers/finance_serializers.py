from django.db.models import QuerySet
from rest_framework import serializers
from .RoomSerializer import RoomTypeListSerializer
from hotel_reservation.models import RoomType, Room, RoomReservation, Reservation


class RoomTypeFinanceSerializer(RoomTypeListSerializer):
    total_profit = serializers.SerializerMethodField()
    total_number_of_room_reserved = serializers.SerializerMethodField()

    class Meta(RoomTypeListSerializer.Meta):
        fields = RoomTypeListSerializer.Meta.fields + ('total_profit', 'total_number_of_room_reserved')

    def get_total_number_of_room_reserved(self, obj: RoomType):
        rooms: QuerySet[Room] = obj.rooms.all()
        number_of_reservations = 0
        for room in rooms:
            number_of_reservations += len(Reservation.objects.filter(room_reservations__room_id=room.id,
                                                                     start_date__gte=self.context.get('start_date'),
                                                                     start_date__lte=self.context.get('end_date'),
                                                                     paid=True, cancelled=False).
                                          values_list('id', flat=True))
        return number_of_reservations

    def get_total_profit(self, obj: RoomType):
        rooms: QuerySet[Room] = obj.rooms.all()
        the_total_profit = 0
        for element in rooms:
            reservation_for_rooms = element.room_reservations.filter(
                reservation__start_date__gte=self.context.get("start_date"),
                reservation__start_date__lte=self.context.get("end_date"),
            reservation__cancelled=False,
            reservation__paid=True)
            cost_for_room = self.total_price_for_rezervations_of_room(reservation_for_rooms, element)
            the_total_profit += cost_for_room
        return the_total_profit

    def total_price_for_rezervations_of_room(self, reservation_for_rooms: QuerySet[RoomReservation], element: Room):
        total_sum = 0
        for room_reservation in reservation_for_rooms:
            reservation = room_reservation.reservation
            if not reservation.cancelled and reservation.paid:
                total_sum += element.online_price if reservation.payment_type == 'online' else element.real_price
        return total_sum
