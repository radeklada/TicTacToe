from django.test import TestCase
from django.contrib.auth.models import User
from ttt import ttt, core, parser
from ttt.models import Game


class StepError(Exception):

    def __init__(self, step, msg):
        self.step = step
        super().__init__(msg)


def execute_scenario(scenario, game, cross_user, circle_user, ensure_valid_scenario=True):
    steps = parser.parse_steps(scenario, ensure_valid=ensure_valid_scenario)
    for step in steps:
        if step['symbol'] == ttt.CROSS_SYMBOL:
            user = cross_user
        else:
            user = circle_user

        try:
            core.update_game(
                game_id=game.id,
                user=user,
                board_nr=step['board_nr'],
                position=step['position']
            )
        except core.MoveError as error:
            raise StepError(step, msg=str(error))



class TTTTest(TestCase):

    def setUp(self):
        self.u1 = User.objects.create_user("u1", "u1@example.com", "haslo123")
        self.u2 = User.objects.create_user("u2", "u2@example.com", "haslo123")
        self.session = core.invite(self.u1, self.u2)
        self.game = core.create_game(self.session)

    def test_invalid_move_on_filled_mini_board(self):
        scenario = '''
            ...|...|...*...|...|...*...|...|...
            ...|X05|...*...|...|...*...|...|...
            ...|...|...*...|...|...*...|...|...
            *** *** *** *** *** *** *** *** ***
            ...|...|...*O04|O08|...*...|...|...
            ...|X07|...*O06|X01|...*...|...|...
            ...|...|...*O02|...|...*...|...|...
            *** *** *** *** *** *** *** *** ***
            ...|...|...*...|...|...*...|...|...
            ...|X03|...*...|...|...*...|...|...
            ...|...|...*...|...|...*...|...|...
        '''
        try:
            execute_scenario(scenario, self.game, cross_user=self.u1, circle_user=self.u2)
        except StepError as error:
            self.assertEquals(error.step['code'], 'O08')
            self.assertEquals('Wrong mini-board, board nr: 5 is filled', str(error))

    def test_allowed_any_mini_board_when_suggested_mini_board_is_filled(self):
        scenario = '''
            ...|...|...*...|...|...*...|...|...
            ...|X05|...*...|...|...*...|...|...
            ...|...|...*...|...|...*...|...|...
            *** *** *** *** *** *** *** *** ***
            ...|...|...*O04|...|...*...|...|...
            ...|X07|...*O06|X01|...*...|...|...
            ...|...|...*O02|...|...*...|...|...
            *** *** *** *** *** *** *** *** ***
            ...|...|...*...|...|...*...|...|...
            ...|X03|...*...|...|...*...|...|...
            ...|...|...*...|...|...*...|...|O08
        '''
        execute_scenario(scenario, self.game, cross_user=self.u1, circle_user=self.u2)
        last_move = core.get_game(self.game.id, self.u1)['moves'][-1]
        self.assertEquals(last_move.board_nr, 9)
        self.assertEquals(last_move.position, 9)
        self.assertEquals(last_move.value, ttt.CIRCLE_SYMBOL)


    def test_win_player_second(self):
        scenario = '''
            X11|...|...*...|...|...*...|...|X05
            ...|O12|X15*...|...|...*...|...|...
            ...|...|X01*...|...|...*O06|...|X09
            *** *** *** *** *** *** *** *** ***
            ...|...|...*O14|...|O04*...|...|...
            ...|...|...*...|X13|...*...|...|O16
            ...|...|...*...|...|...*...|...|X17
            *** *** *** *** *** *** *** *** ***
            ...|...|...*...|...|...*O10|...|O08
            ...|X03|...*...|...|...*O18|...|...
            ...|...|X07*...|...|...*O02|...|...
        '''  # skonczyc
        execute_scenario(scenario, self.game, cross_user=self.u1, circle_user=self.u2)
        updated_game = Game.objects.get(id=self.game.id)
        self.assertEquals(updated_game.result, ttt.CIRCLE_SYMBOL)


    def test_draw(self):
        scenario = '''
            O38|X51|X39*...|...|O06*O50|X45|O40
            X01|X61|X67*O46|O12|X65*X17|O36|X07
            O10|...|X19*O68|...|O52*O58|X23|X41
            *** *** *** *** *** *** *** *** ***
            O18|...|O22*X37|X05|X57*O66|...|O16
            X31|O56|X47*X55|O54|X29*O30|X53|...
            O02|...|O32*O62|X13|X43*O48|...|O08
            *** *** *** *** *** *** *** *** ***
            O60|X11|X49*...|O64|...*X09|O44|X35
            X21|O28|O34*...|O04|...*X33|O42|X15
            X59|X03|X63*X27|O26|O14*O20|X25|O24
        ''' # remis
        try:
            execute_scenario(scenario, self.game, cross_user=self.u1, circle_user=self.u2)
        except StepError as error:
            print("Wykryto błąd", error.step)
            print("message", str(error))
        else:
            updated_game = Game.objects.get(id=self.game.id)
            print("wynik końcowy:", updated_game.result)

