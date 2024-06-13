from rest_framework.permissions import BasePermission

from feedback.models import Feedback
from hotel_reservation.models import Reservation
from users.models import Receptionist, Admin, HotelManager


class ReceptionistPermission(BasePermission):
    def has_permission(self, request, view):
        return Receptionist.objects.filter(user=request.user).exists() or Admin.objects.filter(
            user=request.user).exists() or HotelManager.objects.filter(user=request.user).exists()

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Reservation):
            return True