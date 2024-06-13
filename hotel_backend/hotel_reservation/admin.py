from django.contrib import admin

# Register your models here.
from .models import Room, Reservation, RoomType, GuestInformation

admin.site.register(Room)
admin.site.register(Reservation)
admin.site.register(RoomType)
admin.site.register(GuestInformation)
