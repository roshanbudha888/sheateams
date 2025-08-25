# payment/views.py
from django.shortcuts import render
from datetime import datetime
from payment.models import PaymentRequest
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def payment(request):
    # Get user's recent payment requests
    recent_payments = PaymentRequest.objects.filter(
        user=request.user
    ).order_by("-created_at")[:10]

    context = {
        'recent_payments': recent_payments
    }

    return render(request, 'payment.html', context)



def payment_success(request):
    transaction_id = request.GET.get('transaction_id')
    
    if transaction_id:
        try:
            payment_request = PaymentRequest.objects.get(
                transaction_id=transaction_id,
                status='completed'
            )
            
            context = {
                'payment_details': {
                    'amount': payment_request.amount,
                    'transaction_id': payment_request.transaction_id,
                    'payment_method': payment_request.payment_method,
                    'email': payment_request.email,
                    'completed_at': payment_request.completed_at,
                }
            }
        except PaymentRequest.DoesNotExist:
            context = {
                'error': 'Payment not found or not completed yet'
            }
    else:
        context = {
            'error': 'No transaction ID provided'
        }

    return render(request, 'success.html', context)