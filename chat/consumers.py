import json
import logging
from channels.generic.websocket import (
    AsyncJsonWebsocketConsumer,
)
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.dispatch import receiver
from chat.models import Chat, ChatProfile, Message

User = get_user_model()
logger = logging.getLogger(__name__)


class ActivityConsumer(AsyncJsonWebsocketConsumer):
    groups = ["online_users"]

    async def update_chat_profile_status(self, is_online: bool):
        await ChatProfile.objects.aupdate_or_create(
            user=self.scope["user"],
            defaults={"is_online": is_online},
        )

    async def connect(self):
        self.channel_layer.group_add("online_users", self.channel_name)
        await self.accept()
        await self.update_chat_profile_status(True)
        await self.notify_user_status(user=self.scope["user"], is_online=True)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "online_users",
            self.channel_name,
        )
        await self.update_chat_profile_status(False)
        await self.notify_user_status(user=self.scope["user"], is_online=False)

    async def receive(self, text_data):
        return

    async def notify_user_status(self, user, is_online):
        await self.channel_layer.group_send(
            "online_users",
            {
                "type": "user_status",
                "user_id": user.id,
                "is_online": is_online,
            },
        )

    async def user_status(self, event):
        await self.send_json(event)


class ChatConsumer(AsyncJsonWebsocketConsumer):
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
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
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
