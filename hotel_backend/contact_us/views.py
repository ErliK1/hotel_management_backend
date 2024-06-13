from django.shortcuts import render
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ContactCreateSerializer, ContactListSerializer
from .models import Contact


class ContactCreateAPIView(CreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactCreateSerializer

    def create(self, request, *args, **kwargs):
        response = super(ContactCreateAPIView, self).create(request, *args, **kwargs)
        if response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            pass
            # Do something if needed...
        return response


class ContactListAPIView(ListAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactListSerializer
