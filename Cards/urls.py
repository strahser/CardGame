# urls.py
from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'heroes', views.HeroViewSet)
router.register(r'monsters', views.MonsterViewSet)
router.register(r'skills', views.SkillViewSet)
router.register(r'battle', views.BattleViewSet, basename='battle')

urlpatterns = [
    path('', include(router.urls)),
    path('create_data/', views.create_initial_data, name='create_data'),
    path('start_game/', views.start_game, name='start_game'),
    path('game_play/', views.game_play, name='game_play'),
]