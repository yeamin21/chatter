import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
from chat.middlewares import QueryAuthMiddleware
from chat.routing import websocket_urlpatterns

from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": QueryAuthMiddleware(URLRouter(websocket_urlpatterns)),
        # AllowedHostsOriginValidator(
        # AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        # ),
    }
)
