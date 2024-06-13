from django.contrib import admin

# Register your models here.
from .models import User, HotelManager, Admin, Receptionist, Guest, Cleaner

admin.site.register(User)
admin.site.register(Admin)
admin.site.register(HotelManager)
admin.site.register(Receptionist)
admin.site.register(Guest)
admin.site.register(Cleaner)