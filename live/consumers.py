import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class LiveConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.group      = f'live_{self.session_id}'
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        user = self.scope['user']
        if user.is_authenticated:
            await self.channel_layer.group_send(self.group, {
                'type':     'user_joined',
                'username': user.get_full_name() or user.username,
            })

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope['user']
        if not user.is_authenticated:
            return
        kind = data.get('type', 'message')
        if kind == 'message':
            await self.save_live_message(user, data.get('message', ''))
            await self.channel_layer.group_send(self.group, {
                'type':     'chat_message',
                'message':  data.get('message', ''),
                'username': user.get_full_name() or user.username,
                'initials': user.initials,
                'user_id':  user.id,
            })
        elif kind == 'start_stream' and user.role == 'teacher':
            await self.set_status('live')
            await self.channel_layer.group_send(self.group, {'type': 'stream_started'})
        elif kind == 'end_stream' and user.role == 'teacher':
            await self.set_status('ended')
            await self.channel_layer.group_send(self.group, {'type': 'stream_ended'})

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps(event))

    async def stream_started(self, event):
        await self.send(text_data=json.dumps({'type': 'stream_started'}))

    async def stream_ended(self, event):
        await self.send(text_data=json.dumps({'type': 'stream_ended'}))

    @database_sync_to_async
    def save_live_message(self, user, content):
        from .models import LiveSession, LiveMessage
        try:
            sess = LiveSession.objects.get(id=self.session_id)
            LiveMessage.objects.create(session=sess, sender=user, content=content)
        except LiveSession.DoesNotExist:
            pass

    @database_sync_to_async
    def set_status(self, status):
        from .models import LiveSession
        from django.utils import timezone
        try:
            sess = LiveSession.objects.get(id=self.session_id)
            sess.status = status
            if status == 'live':
                sess.started_at = timezone.now()
            elif status == 'ended':
                sess.ended_at = timezone.now()
            sess.save()
        except LiveSession.DoesNotExist:
            pass
