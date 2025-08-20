from django.urls import path
from . import views
app_name = 'home'

urlpatterns = [
    path('', views.shea_home, name='shea_home'),   # because base.html uses {% url 'shea_game' %}
    
]