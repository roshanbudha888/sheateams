from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.dispatch import receiver
from django.conf import settings
from .models import Message
from django.core.mail import send_mail
from django.db.models.signals import post_save


@receiver(post_save, sender=Message)
def send_message_notification(sender, instance, created, **kwargs):
    if created:
        other_participants = instance.conversation.participants.exclude(id=instance.sender.id)
        
        for participant in other_participants:
            if participant.email:
                try:
                    # Render HTML template
                    conversation_url = f"http://54.225.152.30:8000/chat/"
                    
                    html_content = render_to_string('chat/email_notification.html', {
                        'recipient': participant,
                        'sender': instance.sender,
                        'message': instance,
                        'conversation': instance.conversation,
                        'conversation_url': conversation_url,  # Add this
                    })
                    
                    # Create email
                    email = EmailMultiAlternatives(
                        subject=f'New message from {instance.sender.get_full_name() or instance.sender.username}',
                        body=f'You have a new message from {instance.sender.username}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[participant.email],
                    )
                    email.attach_alternative(html_content, "text/html")
                    email.send()
                    
                except Exception as e:
                    print(f"Failed to send email to {participant.email}: {e}")