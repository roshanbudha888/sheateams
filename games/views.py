from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def games_list(request):
    return render(request, 'game.html')

def game_detail(request, slug):
    return render(request, 'game_detail.html')