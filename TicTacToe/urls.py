"""TicTacToe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ttt import views

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('registration', views.registration, name='registration'),
    path('invite_computer', views.invite_computer_player, name='invite_computer'),
    path('invite', views.invite, name='invite'),
    path('game/<str:external_session_id>', views.current_game, name='current_game'),
    path('game/<str:external_session_id>/<int:game_id>', views.game_details, name='game_details'),
]