from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home_action', views.home, name='home_action'),
    path('create-room', views.create_room, name='create_room'),
    path('join-room', views.join_room, name='join_room'),
    path('profile/<int:user_id>', views.view_profile, name='profile'),
    path('self_profile', views.self_profile_action, name='self_profile'),
    path('photo/<int:profile_id>', views.get_photo, name='photo'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
]
