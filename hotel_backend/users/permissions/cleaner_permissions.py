from rest_framework.permissions import BasePermission

from users.models import Cleaner, Admin, HotelManager


class CleanerPermission(BasePermission):

    def has_permission(self, request, view):
        return Cleaner.objects.filter(user=request.user).exists() or Admin.objects.filter(
            user=request.user).exists() or HotelManager.objects.filter(user=request.user).exists()
