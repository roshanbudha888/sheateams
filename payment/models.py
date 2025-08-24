# payment/models.py
from django.db import models
from django.contrib.auth.models import User



class PaymentRequest(models.Model):
    STATUSES = [
        ('pending', 'Pending'),
        ('qr_sent', 'QR Code Sent'),
        ('completed', "Completed"),
        ('failed', 'Failed')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField()
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    # Link to conversation for easy tracking
    conversation = models.ForeignKey('chat.Conversation', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - ${self.amount} - {self.status}"