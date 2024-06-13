from rest_framework.permissions import BasePermission

from hotel_reservation.models import RoomType, Room
from users.models import HotelManager, Admin


class HotelManagerPermissions(BasePermission):

    def has_permission(self, request, view):
        return HotelManager.objects.filter(user=request.user).exists() or Admin.objects.filter(user=request.user).exists()

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, RoomType):
            return True
        if isinstance(obj, Room):
            return True
        return False

