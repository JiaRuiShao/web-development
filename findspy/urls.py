from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_room', views.create_room, name='create_room'),
    path('get-player', views.get_player, name='get-player'),
    path('join_room', views.join_room, name='join_room'),
    path('profile/<int:user_id>', views.view_profile, name='profile'),
    path('photo/<int:profile_id>', views.get_photo, name='photo'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
]
