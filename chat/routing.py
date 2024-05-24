from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/lobby/", consumers.ActivityConsumer.as_asgi()),
    re_path(
        r"ws/chat/oto/(?P<receiver>\w+)/",
        consumers.ChatConsumer.as_asgi(),
    ),
]
