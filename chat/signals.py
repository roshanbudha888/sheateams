# signals.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.urls import reverse
# Conditional import for Django Sites framework
try:
    from django.contrib.sites.models import Site
    SITES_AVAILABLE = True
except ImportError:
    SITES_AVAILABLE = False
from .models import Message
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def get_conversation_url(participant, conversation_id: int) -> str:
    """Generate appropriate conversation URL based on user type."""
    try:
        if participant.is_superuser:
            # Admin panel URL for superusers - use chat_system_per_user
            url_path = reverse('admin_panel:chat_system_per_user', kwargs={'id': conversation_id})
            print(url_path,"-----")
        else:
            # Regular chat URL for normal users
            url_path = reverse('chat:conversation_detail', kwargs={'conversation_id': conversation_id})
            print(url_path,"mmmmmmm")
        
        # Use Django sites framework for better domain handling
        if SITES_AVAILABLE and hasattr(settings, 'SITE_ID'):
            try:
                current_site = Site.objects.get_current()
                base_url = f"https://{current_site.domain}"
            except:
                base_url = getattr(settings, 'BASE_DOMAIN', 'http://localhost:8000')
        else:
            base_url = getattr(settings, 'BASE_DOMAIN', 'http://localhost:8000')
        
        return f"{base_url.rstrip('/')}{url_path}"
    
    except Exception as e:
        logger.error(f"Error generating conversation URL: {e}")
        # Fallback URL - just go to chat home
        base_url = getattr(settings, 'BASE_DOMAIN', 'http://localhost:8000')
        return f"{base_url}/chat/"

def should_send_notification(participant, message) -> bool:
    """Check if notification should be sent to participant."""
    # Don't send notification to the sender
    if participant.id == message.sender.id:
        return False
    
    # Check if participant has email
    if not participant.email:
        logger.warning(f"No email address for user {participant.username}")
        return False
    
    # Add user preference check if you have notification settings
    if hasattr(participant, 'notification_preferences'):
        if not participant.notification_preferences.email_notifications:
            return False
    
    return True

def get_email_context(recipient, sender, message, conversation, conversation_url) -> dict:
    """Prepare email template context."""
    return {
        'recipient': recipient,
        'sender': sender,
        'message': message,
        'conversation': conversation,
        'conversation_url': conversation_url,
        'site_name': getattr(settings, 'SITE_NAME', 'Your Chat App'),
        'support_email': getattr(settings, 'SUPPORT_EMAIL', settings.DEFAULT_FROM_EMAIL),
    }

def send_notification_email(recipient, sender, message, conversation) -> bool:
    # """Send notification email to a single recipient."""
    try:
        conversation_url = get_conversation_url(recipient, conversation.id)
        
        # Prepare email context
        context = get_email_context(recipient, sender, message, conversation, conversation_url)
        
        # Render HTML content
        html_content = render_to_string('email_notification_template.html', context)
        
        # Create plain text version for better email client compatibility
        text_content = render_to_string('email_notification_template.txt', context)
        
        # Create email subject
        sender_name = sender.get_full_name() or sender.username
        subject_prefix = getattr(settings, 'EMAIL_SUBJECT_PREFIX', '')
        subject = f"{subject_prefix}New message from {sender_name}"
        
        # Create and send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient.email],
            headers={
                'X-Priority': '3',  # Normal priority
                'X-MSMail-Priority': 'Normal',
                'Message-ID': f"<message-{message.id}-{recipient.id}@{getattr(settings, 'EMAIL_MESSAGE_ID_DOMAIN', 'example.com')}>",
            }
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        result = email.send()
        
        if result:
            logger.info(f"Notification sent successfully to {recipient.email} for message {message.id}")
            return True
        else:
            logger.warning(f"Failed to send notification to {recipient.email} for message {message.id}")
            return False
        return True 
    
    except Exception as e:
        logger.error(f"Email notification error for {recipient.email} (message {message.id}): {str(e)}")
        return False

@receiver(post_save, sender=Message)
def send_message_notification(sender, instance, created, **kwargs):
    """Send email notifications for new messages."""
    if not created:
        return
    
    print(f"New message created (ID: {instance.id}), processing notifications...")
    
    # Get other participants (excluding the sender)
    other_participants = instance.conversation.participants.exclude(id=instance.sender.id)
    
    if not other_participants.exists():
        print(f"No other participants to notify for message {instance.id}")
        return
    
    # Track notification results
    successful_notifications = 0
    failed_notifications = 0
    
    for participant in other_participants:
        if should_send_notification(participant, instance):
            success = send_notification_email(
                recipient=participant,
                sender=instance.sender,
                message=instance,
                conversation=instance.conversation
            )
            
            if success:
                successful_notifications += 1
            else:
                failed_notifications += 1
        else:
            logger.debug(f"Skipping notification for {participant.username} (message {instance.id})")
    
    logger.info(f"Notification summary for message {instance.id}: "
                f"{successful_notifications} sent, {failed_notifications} failed")

