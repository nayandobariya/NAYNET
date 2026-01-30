import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import InterviewSession


class InterviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'interview_{self.session_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data['type']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': message_type,
                'data': data,
                'sender_channel': self.channel_name
            }
        )

    # Handle different message types
    async def offer(self, event):
        # Only send to other clients, not back to sender
        if event['sender_channel'] != self.channel_name:
            data = event['data']
            await self.send(text_data=json.dumps({
                'type': 'offer',
                'offer': data['offer']
            }))

    async def answer(self, event):
        if event['sender_channel'] != self.channel_name:
            data = event['data']
            await self.send(text_data=json.dumps({
                'type': 'answer',
                'answer': data['answer']
            }))

    async def ice_candidate(self, event):
        if event['sender_channel'] != self.channel_name:
            data = event['data']
            await self.send(text_data=json.dumps({
                'type': 'ice_candidate',
                'candidate': data['candidate']
            }))

    async def call_request(self, event):
        if event['sender_channel'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'call_request'
            }))

    async def call_accepted(self, event):
        if event['sender_channel'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'call_accepted'
            }))

    async def call_rejected(self, event):
        if event['sender_channel'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'call_rejected'
            }))

    async def call_ended(self, event):
        if event['sender_channel'] != self.channel_name:
            await self.send(text_data=json.dumps({
                'type': 'call_ended'
            }))
