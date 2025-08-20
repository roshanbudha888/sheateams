from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Conversation, Message
from .forms import MessageForm

@login_required
def chat(request):
    # Get all conversations for the current user
    conversations = Conversation.objects.filter(participants=request.user)
    
    # Get users who are not the current user
    users = User.objects.exclude(id=request.user.id)
    
    context = {
        'conversations': conversations,
        'users': users,
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