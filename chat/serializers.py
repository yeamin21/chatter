from rest_framework import serializers

from chat.models import Chat, Message
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class ChatSerializer(serializers.ModelSerializer):
    last_message = MessageSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = "__all__"


class ChatUserSerializer(serializers.ModelSerializer):
    is_online = serializers.BooleanField(default=False)
    last_message = serializers.CharField(read_only=True)
    name = serializers.CharField(source="first_name")

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "is_online",
            "last_message",
        ]
