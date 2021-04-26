import time
import datetime
import json
import random
from statistics import mode, StatisticsError

from django.db import transaction
from django.utils import timezone
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
        room = Room.objects.create(capacity=new_room_capacity, ready=False, phase='')
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
    room.playerTurn = 0
    room.game_end = True
    room.winner = None
    room.msg = None
    room.phase = ''
    room.save()

    player.room = None
    player.save()

    for p in room.player.all():
        p.game_id = None
        p.word = None
        p.identity = None
        p.is_dead = False
        p.vote = None
        p.save()

    for msg in Message.objects.filter(room_id=room.id):
        msg.delete() # clear all message related to the room

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


@login_required
def update_game(request):
    # start the game
    # get the player info
    response_data = []
    player = Player.objects.get(player=request.user)
    room = player.room
    player_turn_id = room.playerTurn
    # print("game end: " + str(room.game_end == True))

    # if room not ready
    if not room.ready:
        for player in room.player.all():
            players ={'room_ready': room.ready,
                      'username': player.player.username,
                      'game_end': room.game_end,
                      }
        response_data.append(players)
        response_json = json.dumps(response_data)
        #print(player_turn_id)
        return HttpResponse(response_json, content_type='application/json')

    # if game end
    elif room.game_end == True:
        # # reset player info
        # for p in room.player.all():
        #     p.game_id = None
        #     p.word = None
        #     p.identity = None
        #     p.is_dead = False
        #     p.vote = None
        #     p.save()
        #
        # # reset room info
        # room.ready = False
        # room.playerTurn = 0
        # room.game_end = True
        # room.winner = None
        # room.msg = None
        # room.phase = ''
        # room.save()

        # reset msg info
        for msg in room.message_set.all():
            msg.content = None
            msg.timestamp = None
            msg.room = None
            msg.player = None
            msg.save()

        for player in room.player.all():
            players = {'room_ready': room.ready,
                       'username': player.player.username,
                       'game_end': room.game_end,
                       }
            response_data.append(players)
        response_json = json.dumps(response_data)
        # print(player_turn_id)
        return HttpResponse(response_json, content_type='application/json')

    # chatting, voting, and display
    else:
        player_turn = Player.objects.get(game_id=player_turn_id, room_id=room.id)
        time_left = room.timeEnd - timezone.now()
        seconds_left = time_left.total_seconds()

        # chatting time
        if room.phase == 'chat':
            # if next player is dead
            if player_turn.is_dead:
                if room.playerTurn == (room.player.count() - 1):
                    # voting (set timeEnd, set playerTurn to 0)
                    room.phase = 'vote'
                    room.timeEnd = timezone.now() + datetime.timedelta(seconds=30)
                    room.playerTurn = 0
                    room.save()
                    #print('player dead, and last player: ' + str(room.timeEnd))

                else:
                    room.playerTurn += 1
                    room.timeEnd = timezone.now() + datetime.timedelta(seconds=30)
                    room.save()
                    #print('player dead, and not last player: ' + str(room.timeEnd))

            # next player not dead
            else:
                if room.timeEnd <= timezone.now():
                    if room.playerTurn == (room.player.count() - 1):
                        # go voting
                        room.phase = 'vote'
                        room.save()
                        #print('not dead player, last player: ' + str(room.timeEnd))
                    else:
                        room.playerTurn += 1
                        room.timeEnd = timezone.now() + datetime.timedelta(seconds=30)
                        room.save()
                        #print('not dead player, not last player: ' + str(room.timeEnd))

        if room.phase == 'display':
            room.timeEnd = timezone.now() + datetime.timedelta(seconds=30)
            room.playerTurn = 0
            room.phase = 'chat'
            room.save()

        for player in room.player.all():
            players = {
                'username': player.player.username,
                'room_timeEnd': room.timeEnd.isoformat(),
                'phase': room.phase,
                'current_time': timezone.now().isoformat(),
                'player_turn_username': player_turn.player.username,
                'current_user_name': player.player.username,
                'player_turn_first_name': player_turn.player.first_name,
                'player_turn_last_name': player_turn.player.last_name,
                'time_left': int(seconds_left),
                'room_ready': room.ready,
                'game_end': room.game_end,
                'is_dead': player.is_dead,
            }
            response_data.append(players)

        response_json = json.dumps(response_data)
        return HttpResponse(response_json, content_type='application/json')


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
    context['profile'] = Profile.objects.get(user=request.user)

    player = Player.objects.get(player=request.user)
    current_profile = Profile.objects.get(user=request.user)
    friends = current_profile.following.all()
    context['friends'] = friends

    if player not in room.player.all():
        if room.capacity == 3 or room.capacity == 5:
            if player.room is None:
                if room.capacity > room.player.count():
                    room.player.add(player)
                    # player.room = room
                    if room.capacity == room.player.count():
                        room.ready = True
                        room.playerTurn = 0
                        room.phase = 'chat'
                        room.timeEnd = timezone.now() + datetime.timedelta(seconds=30)
                        room.game_end = False
                        room.winner = None
                        room.msg = None
                        room.save()

                        for p in room.player.all():
                            p.game_id = None
                            p.word = None
                            p.identity = None
                            p.is_dead = False
                            p.vote = None
                            p.save()

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
            if invited_player.room is None:
                if room.capacity > room.player.count():
                    room.player.add(invited_player)
                    room.save()
                    invited_player.save()

                    message = '<a href="user_mark_all_read">' + 'invite you to a room </a>'
                    notify.send(sender, recipient=invited_friend,
                                verb=message, description=message)

                    # player.room = room
                    if room.capacity == room.player.count():
                        room.ready = True
                        room.playerTurn = 0
                        room.phase = 'chat'
                        room.timeEnd = timezone.now() + datetime.timedelta(seconds=30)
                        room.game_end = False
                        room.winner = None
                        room.msg = None
                        room.save()

                        # print('When first join the room, room.timeEnd: ' + str(room.timeEnd))

                        for p in room.player.all():
                            p.game_id = None
                            p.word = None
                            p.identity = None
                            p.is_dead = False
                            p.vote = None
                            p.save()

                        #print('When first invite friends the room, room.timeEnd: ' + str(room.timeEnd))
                        assign_player_id_words(request,
                                               room)  # assign words and play id for each user in the room

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


@login_required
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
                      timestamp=datetime.datetime.now(), room=room)
    new_msg.save()

    room = player.room
    player_turn_id = room.playerTurn

    if room.playerTurn == (room.player.count() - 1):
        room.phase = 'vote'
        # voting (set timeEnd, set playerTurn to 0)
        room.timeEnd = timezone.now() + datetime.timedelta(seconds=30)
        room.playerTurn = 0
        room.save()
        #print('sending message, last player : ' + str(room.timeEnd))
    else:
        print(room.playerTurn)
        room.playerTurn += 1
        room.timeEnd = timezone.now() + datetime.timedelta(seconds=30)
        room.save()
        #print('sending message, player: ' + str(room.timeEnd))

    return get_msg(request)


@login_required
@ensure_csrf_cookie
def get_msg(request):
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=404)

    player = Player.objects.get(player=request.user)
    room = player.room

    response_data = []
    for msg in Message.objects.filter(room_id=room.id):
        msg = {
            'id': msg.id,
            'content': msg.content,
            'gameID': msg.player.game_id,
            'fname': msg.player.player.first_name,
            'lname': msg.player.player.last_name,
            'timestamp': timezone.localtime(msg.timestamp).strftime('%I:%M %p'),
        }
        response_data.append(msg)

    response_json = json.dumps(response_data)
    return HttpResponse(response_json, content_type='application/json')


@login_required
@ensure_csrf_cookie
def get_vote(request):
    # validate the user who vote and the info passed in request.POST
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=404)
    if not request.POST:
        return _my_json_error_response("You need to use request.POST for this action", status=404)
    if not request.POST['vote'] or not request.POST['vote'].isnumeric():
        return _my_json_error_response("The player id is not valid", status=404)

    # check whether the user type a invalid player id and whether that player id belongs to
    # the players in same the room as request.user
    eliminate_p = get_object_or_404(Player, id=int(request.POST['vote']))
    player = Player.objects.get(player=request.user)
    room = player.room
    room_id = room.id
    players = room.player.all()

    if eliminate_p == 404 or eliminate_p not in players:
        return _my_json_error_response("The player does not exist/is not in this room!", status=404)

    player.vote = int(request.POST['vote'])
    player.save()

    # wait for the others to vote
    # while room.player.filter(vote=None).count() > 0:
    #     time.sleep(1)

    room = Room.objects.get(id=room_id)
    room.voteTime = timezone.now() + datetime.timedelta(seconds=10)
    room.save()

    time.sleep(10)

    return process_vote(request)


@login_required
@ensure_csrf_cookie
def process_vote(request):
    player = Player.objects.get(player=request.user)
    room = player.room
    players = room.player.all()
    print('running')

    if timezone.now() >= room.voteTime:
        print('runningx2')
        # eliminate the user with the most votes
        vote = []

        for p in players:
            vote.append(p.vote)
        try:
            player_eliminate = get_object_or_404(Player, id=mode(vote))
            player_eliminate.is_dead = True
            player_eliminate.save()
            room.msg = 'player ' + player_eliminate.player.first_name + ' ' + \
                       player_eliminate.player.last_name + ' got eliminated this round'
            room.save()
            print(player_eliminate.__dict__)
            print(room)
        except StatisticsError:
            room.msg = 'nobody got eliminated this round'
            room.save()

    else:
        while timezone.now() < room.voteTime:
            time.sleep(1)

    return dump_stats(request)


@login_required
@ensure_csrf_cookie
def dump_stats(request):
    player = Player.objects.get(player=request.user)
    room = player.room
    players = room.player.all()
    response_json = []

    # check how many spy/civilian survive and update the room info
    civilian_left = 0
    mr_white_left = 0
    spy_left = 0
    # civilian = []
    # mr_white = []
    # spy = []
    spy_word = None
    civilian_word = None
    players_alive = []

    players = room.player.all()
    for p in players:
        name = str(p.player.first_name) + str(p.player.last_name)
        print(p.__dict__)
        if p.identity == 'spy':
            spy_word = p.word
            if not p.is_dead:
                players_alive.append(name)
                spy_left += 1

        if p.identity == 'civilian':
            civilian_word = p.word
            if not p.is_dead:
                players_alive.append(name)
                civilian_left += 1

        if (p.identity == 'Mr.White') and (not p.is_dead):
            players_alive.append(name)
            mr_white_left += 1

    print("spy left# ", spy_left)
    print("Mr.White left# ", mr_white_left)
    print("civilian left# ", civilian_left)

    print("the number of mr_white_left ", mr_white_left)
    print("the number of spy_left ", spy_left)
    if mr_white_left + spy_left >= civilian_left:
        room.game_end = True
        room.winner = 'spy'
        room.save()
        print(66666666)
    if mr_white_left + spy_left == 0:
        room.game_end = True
        room.winner = 'civilian'
        room.save()
        print(77777)

    print(room.game_end)
    print('winner' + str(room.winner))

    # if the game end, reset player info
    response_data = []

    for player in players:
        myroom = {
            'room_id': room.id,
            'spy_word': spy_word,
            'civilian_word': civilian_word,
            'game_end': room.game_end,
            'winner': room.winner,
            'msg': room.msg,
            'players_alive': players_alive,
            'username': player.player.username,
            'player_identity': player.identity,
        }
        response_data.append(myroom)
    response_json = json.dumps(response_data)

    # back to display and then chat time
    # time.sleep(10)
    room.phase = 'display'
    room.save()

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
def get_player(request):  # stop calling when room.ready == True! (We'll call get_msg instead)
    # if not user
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=403)

    # get the player info
    response_data = []
    player = Player.objects.get(player=request.user)
    room = player.room

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
            'is_dead': player.is_dead,
            'phase': room.phase,
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