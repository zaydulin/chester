import json
from django.contrib.contenttypes.models import ContentType

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from mainapp.models import Messages
from events.models import Events

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.event_slug = self.scope['url_route']['kwargs']['slug']
        self.event_group_name = 'post_%s' % self.event_slug
        
        await self.channel_layer.group_add(
            self.event_group_name,
            self.channel_name
        )
        
        await self.accept()
        
    async def disconnect(self,code):
         await self.channel_layer.discard(
            self.event_group_name,
            self.channel_name
        )
        
    async def receive(self,text_data):
        text_data_json =  json.loads(text_data)
        message = text_data_json['text']
        
        new_message = await self.create_new_message(message)
        data = {
            'author': new_message.author.username,
            'text': new_message.text
        }
        await self.channel_layer.group_send(
            self.event_group_name,
            {
                'type':'new_message',
                'message': data
            }
        )
        
        
    async def new_message(self,event):
        message = event['message']
        
        await self.send(
            text_data=json.dumps({
                'message':message
            
            })
        
        )
        
    @database_sync_to_async    
    def create_new_message(self,text):
        event = Events.objects.get(slug=self.event_slug)
        new_comment = Messages.objects.create(
            author=self.scope['user'],
            text=text,
            event = event
        )
        return new_comment
    
        
    
