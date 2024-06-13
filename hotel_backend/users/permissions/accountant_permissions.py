from rest_framework.permissions import BasePermission

from users.models import Accountant, Admin, HotelManager

class AccountantPermission(BasePermission):
    def has_permission(self, request, view):
        return Accountant.objects.filter(user=request.user).exists() or Admin.objects.filter(
            user=request.user).exists() or HotelManager.objects.filter(user=request.user).exists()