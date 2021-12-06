from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http.response import Http404

from ttt import core
from ttt.forms import LoginForm, RegistrationForm, InvitationForm
from ttt.serializers import serialized_moves


# Create your views here.
def index(request):
    return render(request, 'index.html')


def registration(request):
    if request.method == 'GET':
        return render(request, 'registration.html', {
            'form': RegistrationForm()
        })
    else:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(**form.cleaned_data)
            auth_login(request, user)
            return redirect(reverse('index'))
        else:
            return render(request, 'registration.html', {
                'form': form
            })


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {
            'form': LoginForm()
        })
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            auth_login(request, form.user)
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return render(request, 'login.html', {
                'form': form
            })


def logout(request):
    auth_logout(request)
    return redirect(reverse('index'))


@login_required
def invite(request):
    if request.method == 'GET':
        return render(request, 'invite.html', {
            'form': InvitationForm(user=request.user)
        })
    else:
        form = InvitationForm(request.POST, user=request.user)
        if form.is_valid():
            core.invite(request.user, form.cleaned_data['player'])
            return redirect(reverse('index'))
        else:
            return render(request, 'invite.html', {
                'form': form
            })


@login_required
def game_session(request, external_session_id):
    game = core.get_game_or_create(external_session_id=external_session_id, user=request.user)
    if game is None:
        raise Http404()
    state = {
        'moves': serialized_moves(core.get_game_moves(game)),
        'result': game.result,
        'your_symbol': core.get_player_symbol(game, request.user)
    }
    return render(request, 'game_session.html', {'game': state})
