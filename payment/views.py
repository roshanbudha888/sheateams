# payment/views.py
from django.shortcuts import render
from datetime import datetime
from payment.models import PaymentRequest
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
import uuid
from decimal import Decimal, InvalidOperation

@login_required
def payment(request):
    # if request.method == 'POST':
    #     try:
    #         # Extract form data
    #         amount = request.POST.get('amount')
    #         email = request.POST.get('email')
    #         payment_method = request.POST.get('payment_method', 'default')
            
    #         # Validate amount
    #         if not amount:
    #             messages.error(request, 'Amount is required')
    #             return redirect('payment:payment')
            
    #         try:
    #             amount_decimal = Decimal(amount)
    #             if amount_decimal <= 0:
    #                 messages.error(request, 'Amount must be greater than 0')
    #                 return redirect('payment')
    #         except (InvalidOperation, ValueError):
    #             messages.error(request, 'Invalid amount format')
    #             return redirect('payment:payment')
            
    #         # Validate email
    #         if not email:
    #             messages.error(request, 'Email is required')
    #             return redirect('payment:payment')
            
    #         # Create payment request
    #         payment_request = PaymentRequest.objects.create(
    #             user=request.user,
    #             amount=amount_decimal,
    #             email=email,
    #             payment_method=payment_method,
    #             transaction_id=str(uuid.uuid4()),
    #             status='pending'
    #         )
            
    #         messages.success(request, f'Payment request created successfully. Transaction ID: {payment_request.transaction_id}')
            
    #         # Redirect to prevent duplicate submissions
    #         return redirect('payment:payment')
            
    #     except Exception as e:
    #         messages.error(request, f'Error creating payment request: {str(e)}')
    #         return redirect('payment:payment')
    
    # GET request - show form and recent payments
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