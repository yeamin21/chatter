from django.shortcuts import render
from rest_framework import viewsets

from chat.models import Chat
from chat.serializers import ChatSerializer


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
