from django.shortcuts import render

def payment(request):
    return render(request, 'payment.html')

def payment_success(request):
    return render(request, 'success.html')