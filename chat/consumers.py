import json

from channels.generic.websocket import (
    AsyncJsonWebsocketConsumer,
)
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from chat.models import Chat, Message

User = get_user_model()


class ActivityConsumer(AsyncJsonWebsocketConsumer):
    groups = []
    active_users = {}

    # @database_sync_to_async
    async def get_user(self, user_id):
        return User.objects.aget(id=user_id)

    async def connect(self):
        await self.accept()
        coroutine_user = await self.get_user(1)
        user = await coroutine_user

        self.active_users[user.id] = {
            "username": user.get_username(),
            "name": user.get_full_name(),
        }

        await self.send_json(self.active_users)

    def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        await self.send_json(text_data)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    groups = []
    active_users = {}

    # @database_sync_to_async
    async def get_user(self, user_id):
        return User.objects.aget(id=user_id)

    async def connect(self):
        receiver_id = self.scope["url_route"]["kwargs"].get("receiver")
        self.room_name = receiver_id
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        existing_chat = (
            await Chat.objects.annotate(
                count_participants=Count(
                    "participants",
                    filter=Q(participants__id__in=[receiver_id, self.scope["user"].id]),
                )
            )
            .filter(count_participants=2)
            .afirst()
        )
        if existing_chat:
            self.chat = existing_chat
        else:
            chat = Chat()
            await chat.asave()
            await chat.participants.aadd(receiver_id, self.scope["user"].id)
            self.chat = chat
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user.offline",
            },
        )

    async def receive(self, text_data):
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": text_data}
        )

    async def chat_message(self, event):
        message = event["message"]
        message = await Message.objects.acreate(
            message=message,
            sender=self.scope["user"],
            chat=self.chat,
        )
        await self.send_json(
            {
                "id": message.id,
                "message": message.message,
                "sender": {
                    "id": message.sender.id,
                    "name": message.sender.get_full_name(),
                },
            }
        )

    async def user_offline(self, event):
        await self.send_json("user offline")
