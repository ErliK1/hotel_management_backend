from rest_framework import serializers

from users.serializers.guest_serializer import GuestListSerializer
from .models import Feedback


class FeedBackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('stars', 'text', 'guest')


class FeedBackListSerializer(serializers.ModelSerializer):
    guest = GuestListSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = ('id', 'stars', 'text', 'guest')

    def get_guest(self, obj: Feedback):
        return f'{obj.guest.user}'


class FeedBackUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('stars', 'text')
        extra_kwargs = {
            'stars': {'allow_null': True,
                      'required': False}
        }


    def update(self, instance: Feedback, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.stars = validated_data.get('stars', instance.stars)
        instance.save()
        return instance
