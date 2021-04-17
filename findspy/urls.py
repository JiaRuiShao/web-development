from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_room', views.create_room, name='create_room'),
    path('get-player/<int:room_id>', views.get_player, name='get-player'),
    path('join_room', views.join_room, name='join_room'),
    path('exit_room', views.exit_room, name='exit_room'),
    path('return_room', views.return_room, name='return_room'),
    path('profile/<int:user_id>', views.view_profile, name='profile'),
    path('photo/<int:profile_id>', views.get_photo, name='photo'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
]
