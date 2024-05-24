from typing import Coroutine, Iterable
from django.db import models

# Create your models here.
# your_app/models.py
from django.contrib.auth.models import User
from django.db import models


class ChatTypeChoices(models.TextChoices):
    ONE_TO_ONE = "OTO", "One-One"
    GROUP = "GRP", "Group"


class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name="chats")
    created_at = models.DateTimeField(auto_now_add=True)
    last_message = models.OneToOneField(
        "Message",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="last_message",
    )
    chat_type = models.CharField(
        max_length=3,
        choices=ChatTypeChoices.choices,
        default=ChatTypeChoices.ONE_TO_ONE,
    )

    def __str__(self):
        return f"Chat {self.id} - {self.created_at}"


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name="messages", on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} from {self.sender} at {self.timestamp}"
