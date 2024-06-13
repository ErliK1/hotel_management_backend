from functools import reduce

from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime

from hotel_reservation.serializers.finance_serializers import RoomTypeFinanceSerializer
from hotel_reservation.models import Room, RoomReservation, Reservation, RoomType



class RoomTypeFinanceListAPIView(ListAPIView):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeFinanceSerializer

    def get(self, request, *args, **kwargs):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if not start_date and end_date:
            return Response({'message': 'Please pass the date'}, status=status.HTTP_400_BAD_REQUEST)
        start_date = datetime.strptime(start_date, "%d/%m/%Y").date()
        end_date = datetime.strptime(end_date, '%d/%m/%Y').date()
        all_types_of_rooms = self.get_queryset()
        context = {
            'start_date': start_date,
            'end_date': end_date,
        }
        serializer_obj = self.get_serializer_class()(all_types_of_rooms, context=context, many=True)
        data = serializer_obj.data
        data.append({'total_profit': self.find_the_total_sum(data)})
        return Response(data, status=status.HTTP_200_OK)

    def find_the_total_sum(self, serializer_data: list):
        return sum([x.get('total_profit') for x in serializer_data])
