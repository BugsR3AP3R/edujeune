import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ClassroomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id    = self.scope['url_route']['kwargs']['room_id']
        self.group_name = f'classroom_{self.room_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope['user']
        if not user.is_authenticated:
            return
        msg = await self.save_message(user, data.get('message', '').strip())
        if not msg:
            return
        await self.channel_layer.group_send(self.group_name, {
            'type':      'chat_message',
            'message':   msg.content,
            'username':  user.get_full_name() or user.username,
            'initials':  user.initials,
            'user_id':   user.id,
            'timestamp': msg.created_at.strftime('%H:%M'),
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, user, content):
        if not content:
            return None
        from .models import Classroom, Message
        try:
            room = Classroom.objects.get(id=self.room_id)
            return Message.objects.create(classroom=room, sender=user, content=content)
        except Classroom.DoesNotExist:
            return None
