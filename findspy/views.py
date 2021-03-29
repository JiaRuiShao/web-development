from django.shortcuts import render, redirect,  get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, Http404
from findspy.models import Profile, Room
from findspy.forms import *


@login_required
def home(request):
    context = {'page_name': 'Home'}
    return render(request, 'findspy/home.html', context)

@login_required
def self_profile_action(request):
    return None


@login_required
def create_room():
    return None


@login_required
def join_room():
    return None


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
            if not profile_form.is_valid():
                context['message'] = 'The data input is not valid. Try again.'
                return render(request, 'findspy/profile.html', context)
            # pic = profile_form.cleaned_data['picture']
            # print('Uploaded picture: {} (type={})'.format(pic, type(pic)))

            profile.picture = profile_form.cleaned_data['picture']
            profile.bio = profile_form.cleaned_data['bio']
            profile.content_type = profile_form.cleaned_data['picture'].content_type
            profile.save()
            context['profile'] = profile

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


def login_action(request):
    context = {'page_name': 'Login'}

    if request.method == 'GET':
        return render(request, 'findspy/login.html', context)

    # get username and password
    if 'username' not in request.POST or 'password' not in request.POST or not request.POST['username'] or not request.POST['password']:
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
    new_profile = Profile(user=new_user)
    new_profile.save()

    # authenticate and login the user
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    login(request, new_user)

    # go back to home page
    return redirect(reverse('home'))