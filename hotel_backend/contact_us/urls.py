from django.urls import path
from .views import ContactListAPIView, ContactCreateAPIView



urlpatterns = [
    path('create/', ContactCreateAPIView.as_view(), name='Reservation_Create'),
    path('list/', ContactListAPIView.as_view(), name='Reservation_List'),
]