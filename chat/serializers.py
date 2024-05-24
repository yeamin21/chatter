from rest_framework import serializers

from chat.models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class ChatSerializer(serializers.ModelSerializer):
    last_message = MessageSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = "__all__"
