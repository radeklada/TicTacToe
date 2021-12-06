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
        last_move = core.get_game_moves(self.game)[-1]
        self.assertEquals(last_move.board_nr, 9)
        self.assertEquals(last_move.position, 9)
        self.assertEquals(last_move.value, ttt.CIRCLE_SYMBOL)


    def test_win_player_second(self):
        scenario = '''
            X11|O24|...*X21|...|...*...|...|X05
            ...|O12|X15*...|...|...*...|...|...
            ...|O22|X01*...|...|...*O06|...|X09
            *** *** *** *** *** *** *** *** ***
            ...|...|...*O14|O20|O04*...|...|...
            ...|X19|...*...|X13|...*...|...|O16
            ...|...|...*...|...|...*...|...|X17
            *** *** *** *** *** *** *** *** ***
            ...|...|...*X23|...|...*O10|...|O08
            ...|X03|...*...|...|...*O18|...|...
            ...|...|X07*...|...|...*O02|...|...
        '''
        execute_scenario(scenario, self.game, cross_user=self.u1, circle_user=self.u2)
        updated_game = Game.objects.get(id=self.game.id)
        self.assertEquals(updated_game.result, ttt.CIRCLE_SYMBOL)


    def test_win_player_first(self):
        scenario = '''
            O20|...|...*...|...|...*X13|...|O12
            ...|O14|...*...|...|...*...|X17|...
            O18|...|O02*...|...|...*...|...|X05
            *** *** *** *** *** *** *** *** ***
            ...|...|X11*X01|...|...*...|...|O16
            ...|...|...*...|X15|...*...|...|...
            O22|...|...*...|...|X07*...|...|X09
            *** *** *** *** *** *** *** *** ***
            X19|...|O04*...|...|...*...|...|...
            ...|X21|...*...|...|...*O10|O06|O08
            ...|...|X23*...|...|...*X03|...|...
        '''
        execute_scenario(scenario, self.game, cross_user=self.u1, circle_user=self.u2)
        updated_game = Game.objects.get(id=self.game.id)
        self.assertEquals(updated_game.result, ttt.CROSS_SYMBOL)


    def test_draw(self):
        scenario =  '''
            ...|...|...*...|X25|...*...|...|O26
            ...|...|...*...|X19|O14*...|O06|...
            X11|X17|X01*...|X23|...*O20|...|...
            *** *** *** *** *** *** *** *** ***
            ...|...|O32*...|X13|X05*X29|...|...
            ...|O28|...*...|X07|...*...|X27|...
            O30|...|...*O08|X03|...*...|...|X15
            *** *** *** *** *** *** *** *** ***
            ...|O18|...*...|O22|...*O10|...|...
            ...|O12|...*...|O04|...*...|O02|...
            X31|X21|X09*...|O24|...*...|...|O16
        '''
        try:
            execute_scenario(scenario, self.game, cross_user=self.u1, circle_user=self.u2, ensure_valid_scenario=True)
        except StepError as error:
            print("Wykryto błąd", error.step)
            print("message", str(error))
        else:
            updated_game = Game.objects.get(id=self.game.id)
            print("wynik końcowy:", updated_game.result)
# skończyć
