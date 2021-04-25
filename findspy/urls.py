from django.urls import path,include
from . import views
import notifications.urls
from django.conf.urls import url

urlpatterns = [
    path('', views.home, name='home'),
    path('create_room', views.create_room, name='create_room'),
    path('get-player/<int:room_id>', views.get_player, name='get-player'),
    path('update_game', views.update_game, name='update_game'),
    path('send-msg', views.send_msg, name='send-msg'),
    path('get-msg', views.get_msg, name='get-msg'),
    path('get-vote', views.get_vote, name='get-vote'),
    path('process_vote', views.process_vote, name='process_vote'),
    path('join_room', views.join_room, name='join_room'),
    path('exit_room', views.exit_room, name='exit_room'),
    path('invite_friend', views.invite_friend, name='invite_friend'),
    path('user_mark_all_read', views.user_mark_all_read, name='user_mark_all_read'),
    path('return_room', views.return_room, name='return_room'),
    path('profile/<int:user_id>', views.view_profile, name='profile'),
    path('photo/<int:profile_id>', views.get_photo, name='photo'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),

]
