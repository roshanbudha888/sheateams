from django.shortcuts import render

def logo(request):
    return render(request, 'logo.html')