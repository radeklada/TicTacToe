from django.db import models
from django.contrib.auth.models import User

from ttt.validators import validate_symbol, validate_position


class Invitation(models.Model):
    external_id = models.CharField(max_length=12, unique=True)
    host = models.ForeignKey(User, on_delete=models.PROTECT)


class GameSession(models.Model):
    external_id = models.CharField(max_length=12, unique=True)
    player_1 = models.ForeignKey(User, on_delete=models.PROTECT, related_name="player_1")
    player_2 = models.ForeignKey(User, on_delete=models.PROTECT, related_name="player_2")


class Game(models.Model):
    session = models.ForeignKey(GameSession, on_delete=models.PROTECT)
    cross_player = models.ForeignKey(User, on_delete=models.PROTECT, related_name="cross_player")
    circle_player = models.ForeignKey(User, on_delete=models.PROTECT, related_name="circle_player")
    created_at = models.DateTimeField()


class Move(models.Model):
    game = models.ForeignKey(Game, on_delete=models.PROTECT)
    position = models.IntegerField(validators=[validate_position])
    symbol = models.CharField(max_length=1, validators=[validate_symbol])

    class Meta:
        unique_together = ["game", "position"]
