from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.contrib.auth.models import User
from chat.models import Conversation

from .models import Game, UserProfile, Transaction, Activity, Message, SystemSettings
from .forms import GameForm

def staff_required(user):
    return user.is_staff

@login_required
@user_passes_test(staff_required)
def admin_dashboard(request):
    total_users = User.objects.count()
    total_games = Game.objects.count()
    total_revenue = Transaction.objects.aggregate(total=Sum('amount'))['total'] or 0
    unread_messages = Message.objects.filter(is_read=False).count()
    
    # Create a sample activity if none exists
    if Activity.objects.count() == 0:
        Activity.objects.create(
            user=request.user,
            description="Logged into the admin dashboard"
        )
    
    recent_activity = Activity.objects.all().order_by('-created_at')[:10]
    
    context = {
        'total_users': total_users,
        'total_games': total_games,
        'total_revenue': total_revenue,
        'unread_messages': unread_messages,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
@user_passes_test(staff_required)
def add_game(request):
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES)
        if form.is_valid():
            game = form.save()
            Activity.objects.create(
                user=request.user,
                description=f"Added new game: {game.title}"
            )
            messages.success(request, 'Game added successfully!')
            return redirect('manage_games')
    else:
        form = GameForm()
    
    return render(request, 'admin_dashboard.html', {'form': form})

@login_required
@user_passes_test(staff_required)
def manage_games(request):
    games = Game.objects.all().order_by('-created_at')
    return render(request, 'admin_dashboard.html', {'games': games})

@login_required
@user_passes_test(staff_required)
def edit_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES, instance=game)
        if form.is_valid():
            form.save()
            Activity.objects.create(
                user=request.user,
                description=f"Edited game: {game.title}"
            )
            messages.success(request, 'Game updated successfully!')
            return redirect('manage_games')
    else:
        form = GameForm(instance=game)

    return render(request, 'admin_dashboard.html', {'form': form, 'game': game})

@login_required
@user_passes_test(staff_required)
def delete_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    
    if request.method == 'POST':
        game_title = game.title
        game.delete()
        Activity.objects.create(
            user=request.user,
            description=f"Deleted game: {game_title}"
        )
        messages.success(request, 'Game deleted successfully!')
        return redirect('manage_games')

    return render(request, 'admin_dashboard.html', {'object': game, 'type': 'game'})

@login_required
@user_passes_test(staff_required)
def add_money(request):
    users = User.objects.all()
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        notes = request.POST.get('notes', '')
        
        try:
            user = User.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
            
            # Create transaction
            transaction = Transaction.objects.create(
                user=user,
                amount=amount,
                payment_method=payment_method,
                notes=notes
            )
            
            # Update user balance
            user_profile.balance += float(amount)
            user_profile.save()
            
            Activity.objects.create(
                user=request.user,
                description=f"Added ${amount} to {user.username}'s account"
            )
            
            messages.success(request, f'Successfully added ${amount} to {user.username}\'s account!')
            return redirect('add_money')
            
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            messages.error(request, 'User not found!')
    
    return render(request, 'admin_dashboard.html', {'users': users})

@login_required
@user_passes_test(staff_required)
def user_profiles(request):
    user_profiles = UserProfile.objects.select_related('user').all()
    return render(request, 'admin_dashboard.html', {'user_profiles': user_profiles})

@login_required
@user_passes_test(staff_required)
def view_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_profile = get_object_or_404(UserProfile, user=user)
    transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:10]
    
    context = {
        'user_profile': user_profile,
        'transactions': transactions,
    }

    return render(request, 'admin_dashboard.html', context)

@login_required
@user_passes_test(staff_required)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        Activity.objects.create(
            user=request.user,
            description=f"Deleted user: {username}"
        )
        messages.success(request, 'User deleted successfully!')
        return redirect('user_profiles')

    return render(request, 'admin_dashboard.html', {'object': user, 'type': 'user'})

@login_required
@user_passes_test(staff_required)
def chat_system(request):
    # Get online users (simplified - in a real app, you'd track online status)
    online_users = Conversation.objects.all()
    
    # Get messages for the current user
    chat_messages = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('timestamp')[:50]
    
    context = {
        'online_users': online_users,
        'chat_messages': chat_messages,
    }
    
    return render(request, 'admin_user_chat.html', context)


@login_required
@user_passes_test(staff_required)
def chat_system_per_user(request, id):
    # Get the conversation by ID
    try:
        selected_conversation = Conversation.objects.get(id=id)
        
        # Get all conversations where current user is a participant
        online_conversations = Conversation.objects.all()
        
        # Get messages for the selected conversation
        chat_messages = selected_conversation.messages.all().order_by('timestamp')[:50]
        
        # Get the other participant in the conversation (for display)
        other_participant = selected_conversation.participants.exclude(
            id=request.user.id
        ).first()
        
    except Conversation.DoesNotExist:
        print("not exists --------------")
        # Handle case where conversation doesn't exist
        online_conversations = Conversation.objects.filter(
            participants=request.user
        ).distinct()
        selected_conversation = None
        chat_messages = []
        other_participant = None
    
    context = {
        'online_users': online_conversations,  # These are actually conversations now
        'chat_messages': chat_messages,
        'selected_user': other_participant,
        'selected_conversation': selected_conversation,
    }

    return render(request, 'admin_user_chat_per_user.html', context)


@login_required
@user_passes_test(staff_required)
@require_POST
@csrf_exempt
def send_message(request):
    try:
        data = json.loads(request.body)
        recipient_id = data.get('recipient_id')
        content = data.get('content')
        
        recipient = get_object_or_404(User, id=recipient_id)
        
        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content
        )
        
        return JsonResponse({
            'status': 'success',
            'message_id': message.id,
            'timestamp': message.timestamp.strftime('%H:%M')
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@user_passes_test(staff_required)
def system_settings(request):
    settings = SystemSettings.load()
    
    if request.method == 'POST':
        settings.system_name = request.POST.get('system_name')
        settings.admin_email = request.POST.get('admin_email')
        settings.currency = request.POST.get('currency')
        settings.max_file_size = int(request.POST.get('max_file_size', 10))
        settings.email_notifications = 'email_notifications' in request.POST
        settings.maintenance_mode = 'maintenance_mode' in request.POST
        settings.save()
        
        Activity.objects.create(
            user=request.user,
            description="Updated system settings"
        )
        
        messages.success(request, 'Settings updated successfully!')
        return redirect('system_settings')
    
    return render(request, 'admin_dashboard.html', {'settings': settings})