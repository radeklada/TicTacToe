import random
import string

from django.utils import timezone

from ttt.models import GameSession, Game


def rand_external_id():
    selected_letters = random.sample(string.ascii_letters, GameSession.EXTERNAL_ID_SIZE)
    return ''.join(selected_letters)


def invite(host_user, guest_user):
    player_1, player_2 = sorted([host_user, guest_user], key=lambda user: user.id)
    return GameSession.objects.create(external_id=rand_external_id(), player_1=player_1, player_2=player_2)


class GameError(Exception):
    pass


def create_game(game_session):
    game = Game.objects.filter(session=game_session).order_by('-created_at').first()
    if game is not None:
        if not game.result:
            raise GameError()
        else:
            cross_player = game.circle_player
            circle_player = game.cross_player
    else:
        cross_player = game_session.player_1
        circle_player = game_session.player_2
    return Game.objects.create(
        session=game_session,
        cross_player=cross_player,
        circle_player=circle_player,
        created_at=timezone.now(),
        result=None
    )
