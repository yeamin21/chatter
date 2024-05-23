import urllib.parse
from django.contrib.auth import get_user_model

User = get_user_model()


class QueryAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def get_user(self, user_id):
        return await User.objects.aget(id=user_id)

    async def __call__(self, scope, receive, send):
        query_string = scope["query_string"].decode()
        query_params = urllib.parse.parse_qs(query_string)
        scope["user"] = await self.get_user(int(query_params["user"][0]))
        return await self.app(scope, receive, send)
