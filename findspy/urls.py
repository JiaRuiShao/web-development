from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_room_5', views.create_room_5, name='create_room_5'),
    path('create_room_3', views.create_room_3, name='create_room_3'),
    path('join_room', views.join_room, name='join_room'),
    path('profile/<int:user_id>', views.view_profile, name='profile'),
    path('self_profile', views.self_profile_action, name='self_profile'),
    path('photo/<int:profile_id>', views.get_photo, name='photo'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
]
