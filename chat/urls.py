from django.urls import include, path, re_path
from rest_framework import routers

from chat.views import ChatViewSet

router = routers.DefaultRouter()
router.register("chats", ChatViewSet)

urlpatterns = [re_path("", include(router.urls))]
