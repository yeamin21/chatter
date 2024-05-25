from django.urls import include, path, re_path
from rest_framework import routers

from chat.views import ChatUserViewSet, ChatViewSet

router = routers.DefaultRouter()
router.register("chats", ChatViewSet)
router.register("users", ChatUserViewSet, basename="chat-user")
urlpatterns = [re_path("", include(router.urls))]
