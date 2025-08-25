# chat/consumer.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Conversation, Message

import base64
import uuid
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

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
            # print(text_data_json,"okokokok")
            message = text_data_json['content']
            image_data = text_data_json.get('image', None)

            # Get sender_id from the authenticated session user
            sender_id = self.scope['user'].id

            # If an image is sent, save it to the Message model
            image_url = None
            if image_data:
                # Save the image to the Message model and get the image object
                message_obj = await self.save_message_with_image(image_data, sender_id)
                image_url = message_obj.image.url
                message = None  # Set message content to image URL
            else:
                # Save the text message only
                message_obj = await self.save_message(message, sender_id)
            

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'content': message,
                    'sender_id': sender_id,
                    'message_id': message_obj.id,
                    'timestamp': message_obj.timestamp.isoformat(),
                    'image_url': image_url
                }
            )
            print("success msg",text_data)
        except Exception as e:
            print(f"Error in receive: {e}",text_data                                                                                                        )
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
        image_url = event.get('image_url', None)

        # Get sender username
        username = await self.get_username(sender_id)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'sender_username': username,
            'message_id': message_id,
            'timestamp': timestamp,
            'image_url': image_url
            
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
    
    # Helper method to save the image to the database (if image is sent)
    @database_sync_to_async
    def save_message_with_image(self, image_data, sender_id):
        # Decode the base64 image string
        format, imgstr = image_data.split(';base64,') 
        image_data = base64.b64decode(imgstr)

        # Create a file name using UUID to avoid conflicts
        file_name = f"{uuid.uuid4()}.png"
        
        # Create a Django ContentFile from the base64 image data
        image_file = ContentFile(image_data)

        # Save the image using Django's default storage (this will save it to 'chat_images/')
        image_path = default_storage.save(f"chat_images/{file_name}", image_file)

        # Now, create the message and save it along with the image
        sender = User.objects.get(id=sender_id)
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            image=f"chat_images/{file_name}",  # Store the image path in the model
            content="",  # For image messages, content is left empty
        )
        # print("success message with image",message)
        return message
    

# chat/consumer.py - Add payment status handling
async def receive(self, text_data):
    try:
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'message')
        
        if message_type == 'payment_verification':
            # Handle payment verification from admin
            await self.handle_payment_verification(text_data_json)
        else:
            # Handle regular messages (your existing code)
            await self.handle_regular_message(text_data_json)
            
    except Exception as e:
        print(f"Error in receive: {e}")
        await self.send(text_data=json.dumps({
            'error': 'Failed to process message'
        }))

async def handle_payment_verification(self, data):
    """Handle payment verification from admin via WebSocket"""
    if not self.scope['user'].is_superuser:
        await self.send(text_data=json.dumps({
            'error': 'Unauthorized'
        }))
        return
    
    transaction_id = data.get('transaction_id')
    action = data.get('action', 'complete')
    
    # You can implement WebSocket-based verification here
    # For now, we'll rely on the HTTP endpoint
    pass

# Add this method to handle payment status updates
async def payment_status_update(self, event):
    """Send payment status updates to WebSocket clients"""
    await self.send(text_data=json.dumps({
        'type': 'payment_status',
        'transaction_id': event['transaction_id'],
        'status': event['status'],
        'message': event['message']
    }))