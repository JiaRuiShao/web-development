import datetime
import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from findspy.models import *
from findspy.forms import *
from notifications.signals import notify
from timeit import default_timer as timer


@login_required
def home(request):
    player = Player.objects.get(player=request.user)
    context = {'page_name': 'Home', 'player': player}

    return render(request, 'findspy/home.html', context)


@login_required
def create_room(request):
    context = {}
    if request.method == 'GET':
        context['error'] = 'You must enter a room to create.'
        return render(request, 'findspy/home.html', context)

    new_room_capacity = 0
    try:
        if 'room_capacity' in request.POST and request.POST['room_capacity'].isnumeric():
            if (int(request.POST.get('room_capacity')) == 3
                    or int(request.POST.get('room_capacity')) == 5):
                new_room_capacity = int(request.POST.get('room_capacity'))

    except Exception:
        context['error'] = 'invalid room capacity'

    player = Player.objects.get(player=request.user)
    current_profile = Profile.objects.get(user=request.user)
    friends = current_profile.following.all()

    if player.room == None:
        room = Room.objects.create(capacity=new_room_capacity, ready=False)
        room.player.add(player)
        room.save()
        # player.room = room # add the room creator into the room

        context = {'room': room, 'players': room.player.all(),
         'friends': friends}
        return render(request, 'findspy/room.html', context)
    else:
        context['error'] = 'You cannot join multiple room at the same time.'
        context['player'] = player

        return render(request, 'findspy/home.html', context)


@login_required
def exit_room(request):
    context = {}
    if request.method == 'GET':
        context['error'] = 'You must a valid room to exit.'
        return render(request, 'findspy/room.html', context)

    if 'exit_room_id' not in request.POST:
        context['error'] = 'The room id is not valid'
        return render(request, 'findspy/room.html', context)

    room_id = request.POST.get('exit_room_id')
    player = Player.objects.get(player=request.user)

    try:
        room = Room.objects.get(id=room_id)
    except Exception:
        context['error'] = 'The room does not exist!'
        return render(request, 'findspy/room.html', context)

    room.ready = False
    room.save()
    player.room = None
    player.game_id = 0
    player.word = None
    player.identity = None
    player.save()

    for msg in Message.objects.filter(player_id = request.user.id):
        msg.delete()

    context['error'] = "You have just exit room " + room_id

    return render(request, 'findspy/home.html', context)


@login_required
def return_room(request):
    context = {}
    if request.method == 'POST':
        context['error'] = 'You need a GET request.'
        return render(request, 'findspy/home.html', context)

    player = Player.objects.get(player=request.user)
    room = player.room
    current_profile = Profile.objects.get(user=request.user)
    friends = current_profile.following.all()

    context['friends'] = friends
    context['room'] = room
    context['players'] = room.player.all()
    
    return render(request, 'findspy/room.html', context)


@login_required
def assign_player_id_words(request, room):
    players = room.player.all()

    f = open('./findspy/words_for_3.json')
    game_sets_for_3 = json.load(f)

    f2 = open('./findspy/words_for_5.json')
    game_sets_for_5 = json.load(f2)

    # add identity assignment
    if players.count() == 3:

        # select a random set
        set_for_3 = random.randrange(0, len(game_sets_for_3))

        # generate spy id
        spy_id = random.randrange(0, players.count())

        # assign id, identity, and word
        i = 0
        for player in players:
            player.game_id = i
            i += 1
            if player.game_id == spy_id:
                player.identity = 'spy'
                player.word = game_sets_for_3[set_for_3][str(0)]
            else:
                player.identity = 'civilian'
                player.word = game_sets_for_3[set_for_3][str(1)]
            player.save()

    elif players.count() == 5:

        # select a random set
        set_for_5 = random.randrange(0, len(game_sets_for_5))

        # generate spy ids (first one as the spy, second one as the Mr.White)
        spy_id = []
        while len(spy_id) < 2:
            my_id = random.randrange(0, players.count())
            if my_id not in spy_id:
                spy_id.append(my_id)

        # assign id, identity, and word
        i = 0
        for player in players:
            player.game_id = i
            i += 1
            if player.game_id == spy_id[0]:
                player.identity = 'spy'
                player.word = game_sets_for_5[set_for_5][str(0)]
            elif player.game_id == spy_id[1]:
                player.identity = 'Mr.White'
                player.word = game_sets_for_5[set_for_5][str(2)]
            else:
                player.identity = 'civilian'
                player.word = game_sets_for_5[set_for_5][str(1)]
            player.save()


def voting(request):
    if request.POST and request.POST['eliminate_id'] and request.POST['eliminate_id'].isnumeric():
        return request.POST['eliminate_id']
    else:
        # some error here
        return None


def update_game(request):
    # start the game
    
    context = {}
    # get the player info
    response_data = []
    room = get_object_or_404(Room, id=room_id)

    players = room.player.all()
    

    for i in range(players.count()):
        print( 'i = ' + str(i))
        if(players[i] == players[players.count()-1]):
            room.save()

        print("player" + " is dead "+ players[i].is_dead)

        if (players[i].is_dead == False ):
                current_player = players[i]

                current_player.save()
                current_typing_player = {
                    'username': current_player.player.username,
                    'room_ready': current_player.room.ready,
                }
                response_data.append(current_typing_player)
                response_json = json.dumps(response_data)
                return HttpResponse(response_json, content_type='application/json')

    context['error'] = 'something wrong!!!'
    return render(request, 'findspy/home.html', context)

        #while len(exist_players_id) > 2:
            #for idx in np.arange(len(exist_players_id)):
                # player#idx typing...(?)
                #start_typing(request, room)
                # set time limit as 30s for each user
                #start = timer()
                #while timer() - start <= 30:
                    #continue
            # player#1 stop typing(?)
            # player#2 typing...
            # player#2 stop typing
            # player#3 typing...
            # player#3 stop typing

            #eliminate_id = voting(request) # this doesn't work
            #exist_players_id.pop(eliminate_id)

            # how to get the eliminated user id(?)
            # remove the player (id) who got eliminated from exist_players_id



@login_required
def join_room(request):
    context = {}
    if request.method == 'GET':
        context['error'] = 'You need a POST request.'
        return render(request, 'findspy/home.html', context)

    # if request.POST['voting'] and request.POST['voting'].isnumeric():
    #     # post the eliminated user id here
    #
    #     context['error'] = 'The room id is not valid'
    #     return render(request, 'findspy/home.html', context)


    if 'room_search_id' not in request.POST or not request.POST['room_search_id'].isnumeric():
        context['error'] = 'The room id is not valid'
        return render(request, 'findspy/home.html', context)

    room_id = request.POST.get('room_search_id')

    try:
        room = Room.objects.get(id=room_id)
    except Exception:
        context['error'] = 'The room does not exist!'
        return render(request, 'findspy/home.html', context)

    context['room'] = room
    context['players'] = room.player.all()
    context['profile'] = Profile.objects.get(user=request.user)

    player = Player.objects.get(player=request.user)
    current_profile = Profile.objects.get(user=request.user)
    friends = current_profile.following.all()
    context['friends'] = friends

    if player not in room.player.all():
        if room.capacity == 3 or room.capacity == 5:
            if player.room == None:
                if room.capacity > room.player.count():
                    room.player.add(player)
                    # player.room = room
                    if room.capacity == room.player.count():
                        room.ready = True
                        room.save()
                        # assign user id, word, identity for each user in the room
                        assign_player_id_words(request, room)
                    context['players'] = room.player.all()
                    return render(request, 'findspy/room.html', context)
                else:
                    context['error'] = 'The room is full.'
                    return render(request, 'findspy/home.html', context)
            else:
                context['error'] = 'You cannot join multiple room at the same time.'
                return render(request, 'findspy/home.html', context)

        else:
            context['error'] = 'This room has a invalid room capacity'
            return render(request, 'findspy/home.html', context)
    else:
        context['error'] = 'You have already been in the room.'
        return render(request, 'findspy/room.html', context)

@login_required
def invite_friend(request):
    context = {}
    if request.method == 'GET':
        context['error'] = 'You need a POST request.'
        return render(request, 'findspy/home.html', context)

    if 'invite_room_id' not in request.POST or not request.POST['invite_room_id'].isnumeric():
        context['error'] = 'The room id is not valid'
        return render(request, 'findspy/home.html', context)

    room_id = request.POST.get('invite_room_id')
    try:
        room = Room.objects.get(id=room_id)
    except Exception:
        context['error'] = 'The room does not exist!'
        return render(request, 'findspy/room.html', context)

    context['room'] = room

    if 'invite_friend_id' not in request.POST or not request.POST['invite_friend_id'].isnumeric():
        context['error'] = 'The friend user does not exist'
        return render(request, 'findspy/room.html', context)

    friend_id = request.POST.get('invite_friend_id')

    context['players'] = room.player.all()
    context['profile'] = Profile.objects.get(user=request.user)

    invited_friend = User.objects.get(id=friend_id)
    invited_player = Player.objects.get(player=invited_friend)

    player = Player.objects.get(player=request.user)
    sender = User.objects.get(username=request.user)
    current_profile = Profile.objects.get(user=request.user)
    friends = current_profile.following.all()
    context['friends'] = friends

    if invited_player not in room.player.all():
        if room.capacity == 3 or room.capacity == 5:
            if invited_player.room == None:
                if room.capacity > room.player.count():
                    room.player.add(invited_player)
                    room.save()
                    invited_player.save()
                    
                    message= '<a href="user_mark_all_read">' + 'invite you to a room </a>'
                    notify.send(sender, recipient=invited_friend, 
                        verb= message, description=message)

                    # player.room = room
                    if room.capacity == room.player.count():
                        room.ready = True
                        room.save()
                        assign_player_id_words(request, room)  # assign words and play id for each user in the room                       

                    context['players'] = room.player.all()
                    return render(request, 'findspy/room.html', context)
                else:
                    context['error'] = 'The room is full.'
                    return render(request, 'findspy/room.html', context)
            else:
                context['error'] = 'This friend cannot join multiple room at the same time.'
                return render(request, 'findspy/room.html', context)

        else:
            context['error'] = 'This room has a invalid room capacity'
            return render(request, 'findspy/room.html', context)
    else:
        context['error'] = 'This friend have already been in the room.'
        return render(request, 'findspy/room.html', context)

def user_mark_all_read(request):
    user = request.user
    notifies = user.notifications.all()
    notifies.mark_all_as_read()
    return redirect(reverse('return_room'))

@login_required
@ensure_csrf_cookie
def send_msg(request):
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=404)
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=404)
    if 'content' not in request.POST or not request.POST['content']:
        return _my_json_error_response("The post content is not valid.", status=404)
    if 'room_id' not in request.POST or not request.POST['room_id']:
        return HttpResponse(status=404)

    content = request.POST['content']
    player = Player.objects.get(player=request.user)
    current_room_id = request.POST['room_id']
    if not current_room_id.isdigit():
        message = 'not valid room_id'
        return HttpResponse(status=404)
    room = get_object_or_404(Room, id=current_room_id)

    new_msg = Message(player=player, content=content, 
        timestamp=datetime.datetime.now(),room = room)
    new_msg.save()

    return get_msg(request)


@login_required
@ensure_csrf_cookie
def get_msg(request):
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=403)

    player = Player.objects.get(player=request.user)
    room = player.room

    response_data = []
    for msg in Message.objects.filter(room_id = room.id):
        msg = {
            'id': msg.id,
            'content': msg.content,
            'gameID': msg.player.game_id,
            'fname': msg.player.player.first_name,
            'lname': msg.player.player.last_name,
            'timestamp': timezone.localtime(msg.timestamp).strftime('%m/%d/%Y %I:%M %p'),
        }
        response_data.append(msg)

    response_json = json.dumps(response_data)
    return HttpResponse(response_json, content_type='application/json')


@login_required
def view_profile(request, user_id):
    profile = Profile.objects.get(user__id=user_id)
    context = {'page_name': 'Profile',
               'profile': profile,
               }

    # for viewing and editing my profile
    if user_id == request.user.id:
        if request.method == 'POST':
            profile_form = ProfileForm(request.POST, request.FILES)
            if profile_form.is_valid():
                
                profile.picture = profile_form.cleaned_data['picture']
                profile.content_type = profile_form.cleaned_data['picture'].content_type
                profile.save()
                context['profile'] = profile

            profile.bio = profile_form.cleaned_data['bio']
            profile.save()

        return render(request, 'findspy/profile.html', context)

    # for viewing and following/unfollowing the others' profile
    view_user = User.objects.get(id=user_id)
    context['view_user'] = view_user

    # request.user's profile object: request.user.profile_user
    if view_user in request.user.profile_user.following.all():
        context['following'] = True
    else:
        context['following'] = False

    if request.method == 'POST':
        if request.POST['follow'] == 'unfollow':
            Profile.objects.get(user=request.user).following.remove(view_user)
            context['following'] = False
        elif request.POST['follow'] == 'follow':
            Profile.objects.get(user=request.user).following.add(view_user)
            context['following'] = True
        else:
            context['message'] = 'Error!'

    return render(request, 'findspy/profile-view.html', context)


@login_required
def get_photo(request, profile_id):
    profile = Profile.objects.get(id=profile_id)
    if not profile.picture:
        raise Http404
    return HttpResponse(profile.picture, content_type=profile.content_type)


@login_required
@ensure_csrf_cookie
def get_player(request, room_id): # stop calling when room.ready == True! (We'll call get_msg instead)
    # if not user
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=403)

    # get the player info
    response_data = []
    room = get_object_or_404(Room, id=room_id)
    for player in room.player.all():
        players = {
            'id': player.id,
            'fname': player.player.first_name,
            'lname': player.player.last_name,
            'game_id': player.game_id,
            'word': player.word,
            'room_ready': player.room.ready,
            'room_id': player.room.id,
            'username': player.player.username,
        }
        response_data.append(players)
    response_json = json.dumps(response_data)
    return HttpResponse(response_json, content_type='application/json')


def _my_json_error_response(message, status=200):
    # You can create your JSON by constructing the string representation yourself (or just use json.dumps)
    response_json = '{ "error": "' + message + '" }'
    return HttpResponse(response_json, content_type='application/json', status=status)


def login_action(request):
    context = {'page_name': 'Login'}

    if request.method == 'GET':
        return render(request, 'findspy/login.html', context)

    # get username and password
    if 'username' not in request.POST or 'password' not in request.POST or not request.POST['username'] or not \
            request.POST['password']:
        context['error'] = "Invalid username/password."
        return render(request, 'findspy/login.html', context)

    username = request.POST['username']
    password = request.POST['password']

    # validate the user info
    user = authenticate(username=username, password=password)
    if not user:
        context['error'] = "Invalid username/password."
        return render(request, 'findspy/login.html', context)

    login(request, user)
    return redirect(reverse('home'))


def logout_action(request):
    logout(request)
    return redirect(reverse('login'))


def register_action(request):
    context = {'page_name': 'Register'}

    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'findspy/register.html', context)

    # creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary
    form = RegisterForm(request.POST)
    context['form'] = form

    # validates the user
    if not form.is_valid():
        return render(request, 'findspy/register.html', context)

    # register and login the user
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    # create profile
    new_profile = Profile.objects.create(user=new_user)
    new_profile.save()

    new_player = Player.objects.create(player=new_user, game_id=None, word=None)
    new_player.save()

    # authenticate and login the user
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    login(request, new_user)

    # go back to home page
    return redirect(reverse('home'))
