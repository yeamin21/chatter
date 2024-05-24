import json

from channels.generic.websocket import (
    AsyncJsonWebsocketConsumer,
)
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.dispatch import receiver
from chat.models import Chat, Message

User = get_user_model()


class ActivityConsumer(AsyncJsonWebsocketConsumer):
    groups = []
    active_users = {}

    async def connect(self):
        await self.accept()
        user = self.scope["user"]
        self.active_users[user.id] = {
            "username": user.get_username(),
            "name": user.get_full_name(),
        }
        await self.send_json(self.active_users)

    async def disconnect(self, close_code):
        user = self.scope["user"]
        self.active_users.pop(user.id)
        await self.send_json(self.active_users)

    async def receive(self, text_data):
        await self.send_json(text_data)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    groups = []
    active_users = {}
    receiver_id: int

    # @database_sync_to_async
    async def get_user(self, user_id):
        return User.objects.aget(id=user_id)

    async def connect(self):
        receiver_id = int(self.scope["url_route"]["kwargs"].get("receiver"))
        self.receiver_id = receiver_id
        self.room_name = receiver_id
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        participants = {receiver_id, self.scope["user"].id}
        existing_chat = (
            await Chat.objects.annotate(
                count_participants=Count(
                    "participants",
                    filter=Q(participants__id__in=list(participants)),
                )
            )
            .filter(count_participants=len(participants))
            .afirst()
        )
        if existing_chat:
            self.chat = existing_chat
        else:
            if (
                receiver_id
                and self.scope["user"].id
                and (receiver_id != self.scope["user"].id)
            ):
                chat = Chat()
                await chat.asave()
                await chat.participants.aadd(*participants)
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
        message = await Message.objects.acreate(
            message=text_data,
            sender=self.scope["user"],
            chat=self.chat,
        )
        self.chat.last_message = message
        await self.chat.asave()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message_id": message.id,
                "message": text_data,
                "sender": {
                    "id": self.scope["user"].id,
                    "name": self.scope["user"].get_full_name(),
                },
            },
        )

    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]
        message_id = event["message_id"]
        await self.send_json(
            {
                "message_id": message_id,
                "message": message,
                "sender": {
                    **sender,
                    "is_me": self.scope["user"].id == sender.get("id"),
                },
            }
        )

    async def user_offline(self, event):
        await self.send_json("user offline")
