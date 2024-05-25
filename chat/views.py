from urllib import request
from django.shortcuts import render
from rest_framework import viewsets

from chat.models import Chat
from chat.serializers import ChatSerializer, ChatUserSerializer
from django.contrib.auth import get_user_model
from django.db.models import F, Prefetch

User = get_user_model()


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer


class ChatUserViewSet(viewsets.ModelViewSet):
    serializer_class = ChatUserSerializer

    def get_queryset(self):
        current_user = self.request.query_params.get("user")
        return (
            User.objects.exclude(id=current_user)
            .prefetch_related(
                Prefetch(
                    "chats",
                    Chat.objects.filter(
                        participants__id__in=[current_user],
                    ),
                )
            )
            .select_related("chat_profile")
            .annotate(
                last_message=F("chats__last_message__message"),
                is_online=F("chat_profile__is_online"),
            )
            .all()
            .values("id", "last_message", "is_online")
        )
