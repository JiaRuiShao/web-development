import json
import random

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import ensure_csrf_cookie
from findspy.models import Profile, Room, Player
from findspy.forms import *


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

    if player.room == None:
        room = Room.objects.create(capacity=new_room_capacity, ready=False)
        room.player.add(player)
        room.save()
        # player.room = room # add the room creator into the room

        context = {'room': room, 'players': room.player.all()}
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

    context['room'] = room
    context['players'] = room.player.all()
    
    return render(request, 'findspy/room.html', context)


@login_required
def assign_player_id_words(request, room):
    players = room.player.all()
    game_sets_for_3 = {
        0: {
            0: "lion",
            1: "tiger"
        },
        1: {
            0: "apple",
            1: "pineapple"
        },
        2: {
            0: "laptop",
            1: "desktop"
        }
    }

    game_sets_for_5 = {
        0: {
            0: "lion",
            1: "tiger",
            2: ""
        },
        1: {
            0: "pineapple",
            1: "apple",
            2: ""
        },
        2: {
            0: "laptop",
            1: "desktop",
            2: ""
        }
    }

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
                player.word = game_sets_for_3[set_for_3][0]
            else:
                player.identity = 'civilian'
                player.word = game_sets_for_3[set_for_3][1]
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
                player.word = game_sets_for_5[set_for_5][0]
            elif player.game_id == spy_id[1]:
                player.identity = 'Mr.White'
                player.word = game_sets_for_5[set_for_5][2]
            else:
                player.identity = 'civilian'
                player.word = game_sets_for_5[set_for_5][1]
            player.save()


@login_required
def join_room(request):
    context = {}
    if request.method == 'GET':
        context['error'] = 'You need a POST request.'
        return render(request, 'findspy/home.html', context)

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

    player = Player.objects.get(player=request.user)
    if player not in room.player.all():
        if room.capacity == 3 or room.capacity == 5:
            if player.room == None:
                if room.capacity > room.player.count():
                    room.player.add(player)
                    # player.room = room
                    if room.capacity == room.player.count():
                        room.ready = True
                        room.save()
                        assign_player_id_words(request, room)  # assign words and play id for each user in the room

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
def view_profile(request, user_id):
    profile = Profile.objects.get(user__id=user_id)
    context = {'page_name': 'Profile',
               # 'profile_form': ProfileForm(instance=Profile.objects.all().get(user__id=user_id)),
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

    # if request.method == 'GET':
    #     return render(request, 'socialnetwork/profile-view.html', context)

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
def get_player(request, room_id):
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=403)

    response_data = []
    room = get_object_or_404(Room, id=room_id)
    for player in room.player.all():
        players = {
            'id': player.id,
            'fname': player.player.first_name,
            'lname': player.player.last_name,
            'game_id': player.game_id,
            'word': player.word,
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
