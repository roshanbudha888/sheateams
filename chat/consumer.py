import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Conversation, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        print("room name ", self.room_group_name)
        
        # Check if user is authenticated and is part of the conversation
        user = self.scope['user']
        if user.is_authenticated and await self.is_participant():
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            print(f"User {user.username} connected to conversation {self.conversation_id}")
        else:
            print("Connection rejected - user not authenticated or not participant")
            await self.close()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"User disconnected from {self.room_group_name}")

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            print(text_data_json,"okokokok")
            message = text_data_json['content']
            
            # Get sender_id from the authenticated session user
            sender_id = self.scope['user'].id
            
            # Save message to database
            message_obj = await self.save_message(message, sender_id)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'content': message,
                    'sender_id': sender_id,
                    'message_id': message_obj.id,
                    'timestamp': message_obj.timestamp.isoformat()
                }
            )
        except Exception as e:
            print(f"Error in receive: {e}")
            await self.send(text_data=json.dumps({
                'error': 'Failed to process message'
            }))

    # Receive message from room group
    async def chat_message(self, event):
        print(event)
        message = event.get('content','none')
        sender_id = event['sender_id']
        message_id = event['message_id']
        timestamp = event['timestamp']

        # Get sender username
        username = await self.get_username(sender_id)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'sender_username': username,
            'message_id': message_id,
            'timestamp': timestamp
        }))

    @database_sync_to_async
    def is_participant(self):
        user = self.scope['user']
        print(f"{user.username} checking participation in conversation {self.conversation_id}")
        
        # Allow superusers to join any conversation
        if user.is_superuser:
            return True
            
        # Check if user is a participant in this conversation
        return Conversation.objects.filter(
            id=self.conversation_id, 
            participants=user
        ).exists()

    @database_sync_to_async
    def save_message(self, content, sender_id):
        sender = User.objects.get(id=sender_id)
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=content
        )
        return message

    @database_sync_to_async
    def get_username(self, user_id):
        user = User.objects.get(id=user_id)
        return user.username