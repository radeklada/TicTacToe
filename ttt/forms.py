from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.urls import reverse
from django.utils.safestring import mark_safe

from ttt import core
from ttt.models import GameSession


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30)
    user = None

    def clean(self):
        if 'username' in self.cleaned_data and 'password' in self.cleaned_data:
            user = authenticate(username=self.cleaned_data['username'],
                                password=self.cleaned_data['password'])
            if user is not None:
                self.user = user
                return
        raise ValidationError("złe hasło lub login")


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=200)

    def clean_username(self):
        exists = User.objects.filter(username__iexact=self.cleaned_data['username']).exists()
        if exists:
            raise ValidationError("Użytkownik istnieje")
        return self.cleaned_data['username']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        exists = User.objects.filter(email__exact=email).exists()
        if exists:
            raise ValidationError("email zajęty")
        return email

# todo: ukryj graczy z ktorymi mamy sesje, ukryj wlasnego gracza
class InvitationForm(forms.Form):
    player = forms.ModelChoiceField(queryset=User.objects
                                    .filter(is_active=True, is_staff=False)
                                    .order_by('username'))

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user


    def clean_player(self):
        player = self.cleaned_data['player']
        if player.id == self._user.id:
            raise ValidationError("zapros innego gracza")
        player_1, player_2 = core.make_players_pair(player, self._user)
        session = GameSession.objects.filter(player_1=player_1, player_2=player_2).first()
        if session is not None:
            url = reverse('game_session', args=[session.external_id])
            raise ValidationError(mark_safe(f'sesja istnieje <a href="{url}"> {session.external_id} </a>'))
        return player