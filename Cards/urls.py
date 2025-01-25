
from django.urls import path, include

from Cards import views

urlpatterns = [
    path('create_data/', views.create_initial_data, name='create_data'),
    path('', views.start_game, name='start_game'),
    path('game_play/', views.game_play, name='game_play'),
]