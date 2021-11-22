import random
import string

from django.utils import timezone
from django.db.models import Q
from django.db import transaction

from ttt.models import GameSession, Game, Move


def rand_external_id():
    selected_letters = random.sample(string.ascii_letters, GameSession.EXTERNAL_ID_SIZE)
    return ''.join(selected_letters)


def invite(host_user, guest_user):
    player_1, player_2 = sorted([host_user, guest_user], key=lambda user: user.id)
    return GameSession.objects.create(external_id=rand_external_id(), player_1=player_1, player_2=player_2)


class GameError(Exception):
    pass


@transaction.atomic()
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


@transaction.atomic()
def get_game(game_id, user):
    game = Game.objects.filter(id=game_id).filter(Q(cross_player=user) | Q(circle_player=user)).first()
    if game is None:
        return None
    moves = list(Move.objects.filter(game_id=game_id))
    return {
        "game": game,
        "moves": moves
    }


def _get_player_symbol(game, user):
    if game.cross_player_id == user.id:
        return Move.CROSS_SYMBOL
    elif game.circle_player_id == user.id:
        return Move.CIRCLE_SYMBOL
    else:
        raise ValueError("unexpected user")


def _next_player_symbol(symbol):
    if symbol == Move.CROSS_SYMBOL:
        return Move.CIRCLE_SYMBOL
    return Move.CROSS_SYMBOL


def _can_move(all_moves, position, symbol):
    opposite_symbol = _next_player_symbol(symbol)
    player_moves = [move for move in all_moves if move.symbol == symbol]
    opposite_player_moves = [move for move in all_moves if move.symbol == opposite_symbol]
    if len(player_moves) > len(opposite_player_moves):
        return False
    for move in all_moves:
        if move.position == position:
            return False
    return True


LINES = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],

    [1, 4, 7],
    [2, 5, 8],
    [3, 6, 9],

    [1, 5, 9],
    [7, 5, 3]
]


def _moves_to_board(moves):
    board = {}
    for move in moves:
        board[move.position] = move.symbol
    return board


def _is_line(board, symbol):
    for a, b, c in LINES:
        if board.get(a) == board.get(b) == board.get(c) == symbol:
            return True
    return False


def _get_result(all_moves, symbol):
    board = _moves_to_board(all_moves)
    if _is_line(board, symbol):
        return symbol
    elif len(all_moves) == Move.POSITIONS:
        return Game.DRAW
    else:
        return None


@transaction.atomic()
def update_game(game_id, user, position):
    game = (Game.objects
            .filter(id=game_id)
            .filter(Q(cross_player=user) | Q(circle_player=user))
            .select_for_update()
            .first())
    if game is None:
        return None
    if game.result is not None:
        return None
    symbol = _get_player_symbol(game, user)
    all_moves = list(Move.objects.filter(game_id=game.id))
    if not _can_move(all_moves, position, symbol):
        return None
    last_move = Move.objects.create(game=game, position=position, symbol=symbol)
    result = _get_result(all_moves + [last_move], symbol)
    if result:
        game.result = result
        game.save()
