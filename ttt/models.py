from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def validate_symbol(value):
    if value != Move.CROSS_SYMBOL and value != Move.CIRCLE_SYMBOL:
        raise ValidationError(f"invalid symbol: {value}")


def validate_position(value):
    if value < Move.MIN_POSITION or Move.MAX_POSITION < value:
        raise ValidationError(f"invalid position: {value}")

def validate_result(value):
    if value != Move.CROSS_SYMBOL and value != Move.CIRCLE_SYMBOL and value != Game.DRAW:
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
    CROSS_SYMBOL = "x"
    CIRCLE_SYMBOL = "o"
    MAX_POSITION = 8
    MIN_POSITION = 0
    game = models.ForeignKey(Game, on_delete=models.PROTECT)
    position = models.IntegerField(validators=[validate_position])
    symbol = models.CharField(max_length=1, validators=[validate_symbol])

    class Meta:
        unique_together = ["game", "position"]
