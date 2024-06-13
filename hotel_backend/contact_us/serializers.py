from rest_framework import serializers
from .models import Contact


class ContactCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('name', 'surname', 'email', 'phone', 'note')


class ContactListSerializer(ContactCreateSerializer):
    class Meta(ContactCreateSerializer.Meta):
        model = Contact
        fields = ('id',) + ContactCreateSerializer.Meta.fields
