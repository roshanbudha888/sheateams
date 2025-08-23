from django.urls import path
from . import views
app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('add-game/', views.add_game, name='add_game'),
    path('manage-games/', views.manage_games, name='manage_games'),
    path('edit-game/<int:game_id>/', views.edit_game, name='edit_game'),
    path('delete-game/<int:game_id>/', views.delete_game, name='delete_game'),
    path('add-money/', views.add_money, name='add_money'),
    path('user-profiles/', views.user_profiles, name='user_profiles'),
    path('view-user/<int:user_id>/', views.view_user, name='view_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('chat/', views.chat_system, name='chat_system'),
    path('chat/<int:id>/', views.chat_system_per_user, name='chat_system_per_user'),

    path('send-message/', views.send_message, name='send_message'),
    path('settings/', views.system_settings, name='system_settings'),
]