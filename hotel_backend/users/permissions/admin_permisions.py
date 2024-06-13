from rest_framework.permissions import BasePermission

from users.models import Admin


class AdminPermission(BasePermission):

    def has_permission(self, request, view):
        return Admin.objects.filter(user=request.user).exists()
