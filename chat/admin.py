from django.contrib import admin

from chat.models import Chat, ChatProfile, Message

admin.site.register([Chat, Message, ChatProfile])
