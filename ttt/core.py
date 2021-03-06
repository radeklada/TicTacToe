import random
import string

from django.utils import timezone
from django.db.models import Q
from django.db import transaction
from django.conf import settings

from ttt.models import GameSession, Game, Move, User
from ttt import ttt


def _rand_external_id():
    selected_letters = random.sample(
        string.ascii_letters,
        GameSession.EXTERNAL_ID_SIZE
    )
    return ''.join(selected_letters)


def make_players_pair(player_1, player_2):
    return sorted(
        [player_1, player_2],
        key=lambda user: user.id
    )


COMPUTER_USERNAME = 'computer'


@transaction.atomic
def invite_computer_player(host_user):
    user = User.objects.filter(username=COMPUTER_USERNAME).first()
    if user is None:
        user = User.objects.create_user(username='computer', email='computer@example.com', password=settings.SECRET_KEY)
    player_1, player_2 = make_players_pair(host_user, user)
    session = GameSession.objects.filter(player_1=player_1, player_2=player_2).first()
    if session is None:
        session = GameSession.objects.create(
            external_id=_rand_external_id(),
            player_1=player_1,
            player_2=player_2
        )
    return session


def invite(host_user, guest_user):
    player_1, player_2 = make_players_pair(host_user, guest_user)
    return GameSession.objects.create(
        external_id=_rand_external_id(),
        player_1=player_1,
        player_2=player_2
    )


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


def get_running_user_games(user):
    return (
        Game.objects
            .select_related()
            .filter(Q(cross_player=user) | Q(circle_player=user))
            .filter(result__isnull=True)
            .order_by('created_at')
    )


def get_game(external_session_id, game_id):
    return Game.objects.filter(session__external_id=external_session_id, id=game_id).first()


def get_game_or_create(external_session_id, user):
    game_session = GameSession.objects.filter(external_id=external_session_id).first()
    if game_session is None or user.id not in (game_session.player_1_id, game_session.player_2_id):
        return None
    game = (
        Game.objects
            .filter(result__isnull=True)
            .filter(session=game_session)
            .filter(Q(cross_player=user) | Q(circle_player=user))
            .first()
    )
    if game is None:
        return create_game(game_session)
    return game


def get_game_moves(game):
    return list(Move.objects.filter(game=game).order_by('id'))


def is_first_player(game, user):
    return user.id == game.cross_player_id


def is_new_game(game):
    return (
        game.result is None and
        not Move.objects.filter(game=game).exists()
    )


def get_computer_player(game):
    if game.cross_player.username == COMPUTER_USERNAME:
        return game.cross_player
    elif game.circle_player.username == COMPUTER_USERNAME:
        return game.circle_player
    else:
        return None


def update_game_by_computer(game, computer_player):
    symbol = get_player_symbol(game, computer_player)
    moves = get_game_moves(game)

    board_nr, pos = ttt.bot_turn(
        boards=ttt.to_boards(moves),
        comp_symbol=symbol,
        next_board_nr=ttt.next_board_nr(moves)
    )

    update_game(game.id, computer_player, board_nr, pos)


class MoveError(Exception):
    pass


def _get_board(game_id, board_nr):
    return ttt.make_board(
        iterable=(
            Move.objects
            .filter(game_id=game_id, board_nr=board_nr)
            .values_list('position', 'value')
        ),
        mini=board_nr != ttt.MAIN_BOARD_NR
    )


def _update_board(game, board_nr, position, value):
    if not ttt.is_pos(position):
        raise MoveError('Invalid position: {}'.format(position))

    board = _get_board(game.id, board_nr)

    if board[position]:
        raise MoveError('The position {} is occupied'.format(position))

    Move.objects.create(
        game=game, board_nr=board_nr,
        position=position, value=value
    )
    board[position] = value

    return ttt.get_board_result(board)


def _update_mini_board(game, board_nr, position, symbol):
    if not ttt.is_mini_board_nr(board_nr):
        raise MoveError('Invalid mini-board nr: {}'.format(board_nr))

    if not ttt.is_symbol(symbol):
        raise MoveError('Invalid symbol, got: {}'.format(symbol))

    prev_move = _get_last_player_move(game)
    main_board = _get_board(game.id, ttt.MAIN_BOARD_NR)

    if prev_move is None and symbol == ttt.CIRCLE_SYMBOL:
        raise MoveError('Required cross symbol')

    if prev_move and prev_move.value == symbol:
        raise MoveError('Required the next symbol, got: {}'.format(symbol))

    expected_board_nr = (prev_move.position if prev_move and main_board[prev_move.position] is None else None)
    print(expected_board_nr)
    if expected_board_nr and expected_board_nr != board_nr:
        raise MoveError('Wrong mini-board, expected: {}, got: {}'.format(
            prev_move.position, board_nr))

    print(main_board[board_nr])
    if main_board[board_nr]:
        raise MoveError('Wrong mini-board, board nr: {} is filled'.format(board_nr))

    return _update_board(game, board_nr, position, symbol)


def _update_main_board(game, position, result):
    if not ttt.is_result(result):
        raise Exception('Invalid result, got: {}'.format(result))
    return _update_board(game, ttt.MAIN_BOARD_NR, position, result)


def _get_game_to_update_by_user(game_id, user):
    # select for update zaklada blokade
    game = Game.objects.select_for_update().get(id=game_id)
    if game.cross_player_id != user.id and game.circle_player_id != user.id:
        raise GameError('Unexpected player {} in the game {}: '.format(
            user.id, game.id))
    if game.result:
        raise GameError('The game is finished')
    return game


def get_player_symbol(game, user):
    if game.cross_player_id == user.id:
        return ttt.CROSS_SYMBOL
    elif game.circle_player_id == user.id:
        return ttt.CIRCLE_SYMBOL
    else:
        raise ValueError("unexpected user")


def is_player_move(moves, player_symbol):
    n = sum([1 for m in moves if m['board_nr'] != ttt.MAIN_BOARD_NR])
    return (
        (player_symbol == ttt.CROSS_SYMBOL and n % 2 == 0) or
        (player_symbol == ttt.CIRCLE_SYMBOL and n % 2 == 1)
    )


def _get_last_player_move(game):
    return (
        Move.objects
            .exclude(board_nr=ttt.MAIN_BOARD_NR)
            .filter(game_id=game.id, board_nr__gt=ttt.MAIN_BOARD_NR)
            .order_by('-id')
            .first()
    )


@transaction.atomic()
def update_game(game_id, user, board_nr, position):
    game = _get_game_to_update_by_user(game_id, user)
    symbol = get_player_symbol(game, user)
    result = _update_mini_board(game, board_nr, position, symbol)
    if result:
        game_result = _update_main_board(game, board_nr, result)
        if game_result:
            game.result = result
            game.save()

