# chat/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Conversation, Message
from .forms import MessageForm

import json
from django.views.decorators.http import require_http_methods
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from payment.models import PaymentRequest
import uuid
from datetime import datetime
from django.utils import timezone

# @login_required
# def chat(request):
#     # Get all conversations for the current user
#     conversations = Conversation.objects.get_or_create(participants=request.user)
    
#     # Get users who are not the current user
#     users = User.objects.exclude(id=request.user.id)
    
#     context = {
#         'conversations': conversations,
#         'users': users,
#     }
#     return render(request, 'chat.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Conversation, Message

@login_required
def chat(request):
    # Get or create conversation between current user and admin
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        return render(request, 'chat.html', {'error': 'No admin user found'})
    
    # Get or create conversation between current user and admin
    conversation, created = Conversation.objects.get_or_create(
        name=f"Chat between Admin and {request.user.username}"
    )
    
    # Add participants if this is a new conversation
    if created:
        conversation.participants.add(request.user, admin_user)
    
    # Get messages for this conversation
    messages = conversation.messages.all().order_by('timestamp')
    
    context = {
        'conversation': conversation,
        'messages': messages,
        'admin_user': admin_user,
        'room': conversation,  # Add this for template compatibility
        'current_user': request.user,
    }
    return render(request, 'chat.html', context)

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    # Mark messages as read
    Message.objects.filter(conversation=conversation).exclude(sender=request.user).update(is_read=True)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            return redirect('chat:conversation_detail', conversation_id=conversation.id)
    else:
        form = MessageForm()
    
    messages = conversation.messages.all()
    
    context = {
        'conversation': conversation,
        'messages': messages,
        'form': form,
        'other_user': conversation.participants.exclude(id=request.user.id).first()
    }
    return render(request, 'admin_chat.html', context)

# Add the missing start_conversation view
@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Check if conversation already exists
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()
    
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
    
    return redirect('chat:conversation_detail', conversation_id=conversation.id)

# Add the missing get_unread_count view
@login_required
def get_unread_count(request):
    unread_count = Message.objects.filter(
        conversation__participants=request.user
    ).exclude(sender=request.user).filter(is_read=False).count()
    
    return JsonResponse({'unread_count': unread_count})


# Integration of payment and chat
@login_required
@require_http_methods(["POST"])
def send_payment_request(request):
    try:
        data = json.loads(request.body)
        amount = data.get('amount')
        email = data.get('email')
        payment_method = data.get('payment_method')

        # Validate input
        if not amount or float(amount) <= 0:
            return JsonResponse({'success': False, 'error':"Invalid amount"})

        # Get or create conversation with admin
        admin_user = User.objects.filter(is_superuser=True).first()

        if not admin_user:
            return JsonResponse({'success': False, 'error': 'No admin user found'})
        
        conversation, created = Conversation.objects.get_or_create(name=f"Chat between Admin and {request.user.username}")

        if created:
            conversation.participants.add(request.user, admin_user)
            
        # Create PaymentRequest immediately with 'pending' status
        transaction_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"

        payment_request = PaymentRequest.objects.create(
            user=request.user,
            amount=amount,
            email=email,
            payment_method=payment_method.upper(),
            transaction_id=transaction_id,
            status='pending',
            conversation=conversation
        )
        # Simple payment request message
        payment_message = f"""PAYMENT REQUEST
Transaction ID: {transaction_id}
Amount: ${amount}
Email: {email}
Payment Method: {payment_method.upper()}
From: {request.user.username}

Please send QR code for payment."""
        
        # Save message to database
        message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=payment_message
            )
            

            # Send to admin via WebSocket if they are online
        channel_layer = get_channel_layer()
        room_group_name = f'chat_{conversation.id}'
        
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type':'chat_message',
                'content':payment_message,
                'sender_id':request.user.id,
                'message_id':message.id,
                'timestamp': message.timestamp.isoformat()
                }
            )
        return JsonResponse({
            'success': True,
            'transaction_id': transaction_id,
            })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
# Admin Verification View
@login_required
@require_http_methods(["POST"])
def verify_payment(request):
    """Admin endpoint to verify payment completion"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Unauthorized - Admin access required'})
    
    try:
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        action = data.get('action', 'complete')
        
        if not transaction_id:
            return JsonResponse({'success': False, 'error':'Transaction ID required'})
        
        # Get the pending payment request
        payment_request = PaymentRequest.objects.get(
            transaction_id=transaction_id,
            status__in=['pending','qr_sent']
        )

        # Update status based on action
        if action == 'complete':
            payment_request.status = 'completed'
            payment_request.completed_at = timezone.now()
            status_message = "COMPLETED"
            user_message = f"""PAYMENT CONFIRMED

Transaction ID: {transaction_id}
Amount: ${payment_request.amount}
Status: COMPLETED

Your payment has been verified and processed successfully!
You can now access your services."""
        else:
            payment_request.status = 'failed'
            user_message = f"""PAYMENT FAILED
Transaction ID: {transaction_id}
Amount: ${payment_request.amount}
Status: FAILED

Payment verification failed. Please contact support or try again."""
            payment_request.save()

            # Send confirmation message to user via WebSocket
            conversation = payment_request.conversation

            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=user_message
            )

            # Send via WebSocket to notify user
            channel_layer = get_channel_layer()
            room_group_name = f'chat_{conversation.id}'

            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'chat_message',
                    'content': user_message,
                    'message_id': message.id,
                    'timestamp': message.timestamp.isoformat()
                }
            )

            return JsonResponse({
                'success': True,
                'status': payment_request.status,
                'message':f'Payment {payment_request.status}'
            })
    except PaymentRequest.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Payment request not found or already processed'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
