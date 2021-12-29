import json

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http.response import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ttt import core, ttt
from ttt.forms import LoginForm, RegistrationForm, InvitationForm
from ttt.serializers import serialized_moves, deserialized_user_move


# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return render(request, 'index.html')
    games = core.get_running_user_games(request.user)
    return render(request, 'index.html', {'games': games})


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
def invite_computer_player(request):
    session = core.invite_computer_player(request.user)
    return redirect(reverse('current_game', args=[session.external_id]))


@csrf_exempt
@login_required
def current_game(request, external_session_id):
    game = core.get_game_or_create(external_session_id=external_session_id, user=request.user)
    if game is None:
        raise Http404()
    return redirect(reverse('game_details', args=[external_session_id, game.id]))


@csrf_exempt
@login_required
def game_details(request, external_session_id, game_id):
    game = core.get_game(external_session_id, game_id)
    if game is None:
        raise Http404()

    if request.method == 'GET':
        state = {
            'moves': serialized_moves(core.get_game_moves(game)),
            'result': game.result,
            'your_symbol': core.get_player_symbol(game, request.user)
        }
        fields = ttt.to_rows(ttt.all_boards_positions(), row_size=9)
        return render(request, 'game_session.html', {
            'game': state,
            'fields': fields,
            'external_session_id': external_session_id})
    else:
        try:
            user_data = json.loads(request.body.decode('utf-8'))
        except ValueError:
            return JsonResponse({'error': 'invalid json'}, status=400)

        try:
            user_move = deserialized_user_move(user_data)
        except ValueError as exc:
            return JsonResponse({'error': str(exc)}, status=400)

        try:
            core.update_game(game.id, request.user, **user_move)
        except core.MoveError as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        except core.GameError:
            return JsonResponse({'error': 'ignored'}, status=400)

        return JsonResponse({}, status=200)

