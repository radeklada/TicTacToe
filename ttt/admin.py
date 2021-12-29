from django.contrib import admin
from ttt.models import GameSession, Move

# Register your models here.
admin.site.register(GameSession)
admin.site.register(Move)