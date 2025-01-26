# views.py
from django.shortcuts import render, redirect
from .models import Hero, Monster, Skill, CharacterType
from .battle_state import BattleState, CardState, SkillState
import logging
from rest_framework import viewsets
from .serializers import HeroSerializer, MonsterSerializer, SkillSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django.urls import reverse

# Создаем логгер
logger = logging.getLogger(__name__)


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class HeroViewSet(viewsets.ModelViewSet):
    queryset = Hero.objects.all()
    serializer_class = HeroSerializer


class MonsterViewSet(viewsets.ModelViewSet):
    queryset = Monster.objects.all()
    serializer_class = MonsterSerializer


class BattleViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def monster_turn(self, request):
        if 'battle_state' not in request.session:
            return Response({"message": "Игра не начата"}, status=400)
        battle_state = BattleState.from_dict(request.session['battle_state'])
        battle_state.process_monster_turn()
        request.session['battle_state'] = battle_state.to_dict()
        return Response(battle_state.to_dict())


def create_initial_data(request):
    """Создает начальные данные (героев и монстров) если их нет."""

    if Hero.objects.exists() or Monster.objects.exists():
        return render(request, 'Cards/data_created.html', {'message': 'Данные уже созданы!'})

    heroes_data = [
        {"name": "Герой 1", "health": 100, "attack": 15, "initiative": 7,
         'skills': [{'name': 'Мощный удар', 'damage': 25}]},
        {"name": "Герой 2", "health": 80, "attack": 10, "initiative": 9, 'skills': [{'name': 'Лечение', 'damage': 20}]},
        {"name": "Герой 3", "health": 120, "attack": 8, "initiative": 5, 'skills': [{'name': 'Защита', 'damage': 25}]},
    ]
    monsters_data = [
        {"name": "Монстр 1", "health": 50, "attack": 10, "initiative": 6, 'skills': [{'name': 'Укус', 'damage': 15}]},
        {"name": "Монстр 2", "health": 60, "attack": 8, "initiative": 5, 'skills': [{'name': 'Ранение', 'damage': 20}]},
        {"name": "Монстр 3", "health": 70, "attack": 12, "initiative": 4, 'skills': [{'name': 'Яд', 'damage': 10}]},
    ]

    # Создаем все навыки
    all_skills = {}
    for data in heroes_data + monsters_data:
        for skill_data in data.get('skills', []):
            skill, created = Skill.objects.get_or_create(**skill_data)
            all_skills[skill_data['name']] = skill

    # Создаем всех героев и добавляем навыки
    for hero_data in heroes_data:
        hero = Hero.objects.create(
            name=hero_data['name'],
            health=hero_data['health'],
            attack=hero_data['attack'],
            initiative=hero_data['initiative'],
        )
        for skill_data in hero_data['skills']:
            hero.skills.add(all_skills[skill_data['name']])

    # Создаем всех монстров и добавляем навыки
    for monster_data in monsters_data:
        monster = Monster.objects.create(
            name=monster_data['name'],
            health=monster_data['health'],
            attack=monster_data['attack'],
            initiative=monster_data['initiative'],
        )
        for skill_data in monster_data.get('skills', []):
            monster.skills.add(all_skills[skill_data['name']])

    return render(request, 'Cards/data_created.html', {'message': 'Данные успешно созданы!'})


def start_game(request):
    """Начинает новую игру"""
    if request.method == 'POST':
        # Очищаем сессию
        if 'battle_state' in request.session:
            del request.session['battle_state']
        # Получаем героев и монстров из БД
        heroes = list(Hero.objects.all())
        monsters = list(Monster.objects.all())

        # Создаем BattleState
        participants = [
                           CardState(
                               id=hero.id,
                               name=hero.name,
                               health=hero.health,
                               attack=hero.attack,
                               initiative=hero.initiative,
                               active=hero.active,
                               is_character_type=hero.is_character_type,
                               skills=[SkillState(name=skill.name, damage=skill.damage) for skill in hero.skills.all()]
                           ) for hero in heroes
                       ] + [
                           CardState(
                               id=monster.id,
                               name=monster.name,
                               health=monster.health,
                               attack=monster.attack,
                               initiative=monster.initiative,
                               active=monster.active,
                               is_character_type=monster.is_character_type,
                               skills=[SkillState(name=skill.name, damage=skill.damage) for skill in
                                       monster.skills.all()]
                           ) for monster in monsters
                       ]
        battle_state = BattleState(participants=participants, battle_log="")

        logger.debug(battle_state.to_dict())  # Использем наш логгер
        # Сериализуем все данные
        request.session['battle_state'] = battle_state.to_dict()

        return redirect('game_play')
    return render(request, 'Cards/start_game.html')


def game_play(request):
    if 'battle_state' not in request.session:
        return redirect('start_game')

    battle_state = BattleState.from_dict(request.session['battle_state'])

    if battle_state.is_battle_over():
        del request.session['battle_state']
        return render(request, 'Cards/game_play.html', {'battle': battle_state,
                                                        'message': 'Игра окончена. Обновите страницу для новой игры.',
                                                        'game_over': True})

    current_participant = battle_state.get_active_participant()

    if request.method == 'POST' and current_participant:
        action = request.POST.get('action')
        hero_id = request.POST.get('hero_id')
        target_id = request.POST.get('target_id')
        skill_index = request.POST.get('skill_index', None)

        if current_participant.is_character_type == 'HERO' and current_participant.health > 0:
            battle_state.process_hero_turn(hero_id, target_id, action, skill_index)
            battle_state.handle_monster_turns()
            request.session['battle_state'] = battle_state.to_dict()

    # Начинаем новый раунд, если все персонажи сделали ход
    if not battle_state.get_active_participant():
        battle_state.start_new_round()
        request.session['battle_state'] = battle_state.to_dict()

    # Получаем участников для рендера
    participants = battle_state.participants
    current_participant = battle_state.get_active_participant()

    return render(request, 'Cards/game_play.html',
                  {'battle': battle_state, 'participants': participants,
                   'current_participant': current_participant, 'game_over': False})