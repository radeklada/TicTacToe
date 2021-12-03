from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from ttt import ttt


def validate_position(value):
    if not ttt.is_pos(value):
        raise ValidationError(f"invalid position: {value}")


def validate_board(value):
    if not ttt.is_board(value):
        raise ValidationError(f"invalid board: {value}")


def validate_result(value):
    if not ttt.is_result(value):
        raise ValidationError(f"Invalid result: {value}")


class GameSession(models.Model):
    EXTERNAL_ID_SIZE = 12
    external_id = models.CharField(max_length=EXTERNAL_ID_SIZE, unique=True)
    player_1 = models.ForeignKey(User, on_delete=models.PROTECT, related_name="player_1")
    player_2 = models.ForeignKey(User, on_delete=models.PROTECT, related_name="player_2")

    class Meta:
        unique_together = ["player_1", "player_2"]


class Game(models.Model):
    DRAW = "d"
    session = models.ForeignKey(GameSession, on_delete=models.PROTECT)
    cross_player = models.ForeignKey(User, on_delete=models.PROTECT, related_name="cross_player")
    circle_player = models.ForeignKey(User, on_delete=models.PROTECT, related_name="circle_player")
    created_at = models.DateTimeField()
    result = models.CharField(max_length=1, validators=[validate_result], null=True)


class Move(models.Model):
    game = models.ForeignKey(Game, on_delete=models.PROTECT)
    board_nr = models.IntegerField(validators=[validate_board])
    position = models.IntegerField(validators=[validate_position])
    value = models.CharField(max_length=1, validators=[validate_result])

    class Meta:
        unique_together = ["game", "board_nr", "position"]
