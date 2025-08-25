# chat/urls.py
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat, name='chat'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('start/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('unread/count/', views.get_unread_count, name='unread_count'),
    
    # Payment message:
    path('send-payment-request/', views.send_payment_request, name='send_payment_request'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
]