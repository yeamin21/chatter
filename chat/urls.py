from django.urls import include, path, re_path
from rest_framework import routers

from chat.views import ChatUserViewSet, ChatViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register("chats", ChatViewSet)
router.register("messages", MessageViewSet, basename="chat-message")
router.register("users", ChatUserViewSet, basename="chat-user")
urlpatterns = [re_path("", include(router.urls))]
