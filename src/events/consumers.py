# consumers.py
import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from mainapp.models import Messages
from events.models import Events


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.event_slug = None
        self.event_group_name = "post_%s" % self.event_slug

    async def connect(self):
        self.event_slug = self.scope["url_route"]["kwargs"]["slug"]
        await self.channel_layer.group_add(self.event_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.event_group_name, self.channel_name)
        await super().disconnect(code=code)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["text"]

        new_message = await self.create_new_message(message)
        data = {"user": new_message.user.username,"avatar":new_message.user.avatar.url, "message": new_message.message,"home_score":new_message.event.home_score,"away_score":new_message.event.away_score,"last_incident":new_message.event}
        await self.channel_layer.group_send(self.event_group_name, {"type": "new_message", "message": data})

    async def new_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))

    @database_sync_to_async
    def create_new_message(self, text):
        event = Events.objects.get(slug=self.event_slug)
        new_comment = Messages.objects.create(user=self.scope["user"], message=text, event=event)
        return new_comment
