from rest_framework.permissions import BasePermission

from feedback.models import Feedback
from hotel_reservation.models import Reservation
from users.models import Guest, Admin, HotelManager


class GuestPermission(BasePermission):

    def has_permission(self, request, view):
        return Guest.objects.filter(user=request.user).exists() or Admin.objects.filter(
            user=request.user).exists() or HotelManager.objects.filter(user=request.user).exists()

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Reservation):
            return obj.guest_user == request.user.guest
        if isinstance(obj, Feedback):
            return obj.guest == request.user.guest
        return False

class GuestOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        return Guest.objects.filter(user=request.user).exists()

    def has_object_permission(self, request, view, obj):
        return obj.guest == Guest.objects.get(user=request.user)
