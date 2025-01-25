# views.py
from django.shortcuts import render, redirect
from .models import Hero, Monster, Battle
import random
import json

import logging
logging.basicConfig(level=logging.DEBUG,
                    filename="app.log",
                    filemode="w",  # "a" для добавления, "w" для перезаписи
                    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

logger = logging.getLogger(__name__)

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
        {"name": "Монстр 1", "health": 50, "attack": 10, "initiative": 6},
        {"name": "Монстр 2", "health": 60, "attack": 8, "initiative": 5},
        {"name": "Монстр 3", "health": 70, "attack": 12, "initiative": 4},
    ]

    heroes = [Hero.objects.create(**data) for data in heroes_data]
    monsters = [Monster.objects.create(**data) for data in monsters_data]

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

        battle = Battle()
        battle.heroes = heroes # записываем id героев
        battle.monsters = monsters # записываем id монстров
        battle.current_turn = 0
        battle.battle_log = ""
        # Сериализуем все данные
        request.session['battle_state'] = battle.to_dict()

        return redirect('game_play')
    return render(request, 'Cards/start_game.html')


def game_play(request):
    """Отображает текущее состояние боя и обрабатывает действия игрока"""
    if 'battle_state' not in request.session:
        return redirect('start_game')

    battle_data = request.session['battle_state']
    battle = Battle.from_dict(battle_data)

    # Получаем активных участников
    participants = battle.determine_turn_order(active_only=True)

    # Обработка окончания боя
    if battle.battle_over():
        del request.session['battle_state']
        return render(request, 'Cards/game_play.html', {'battle': battle, 'message': 'Игра окончена. Обновите страницу для новой игры.', 'game_over': True})

    # Обработка хода игрока
    current_participant = participants[battle.current_turn % len(participants)] if participants else None

    if request.method == 'POST' and current_participant and not current_participant['is_monster']:
        action = request.POST.get('action')
        hero_id = request.POST.get('hero_id')
        target_id = request.POST.get('target_id')
        skill_index = request.POST.get('skill_index', None)

        hero = next((h for h in battle.heroes if h.id == int(hero_id)), None)
        target = next((m for m in battle.monsters if m.id == int(target_id)), None)

        if action == 'attack':
            message = hero.normal_attack(target)
            battle.battle_log += f"\n{message}"
        elif action == 'skill' and skill_index is not None:
            message = hero.use_skill(int(skill_index), target)
            battle.battle_log += f"\n{message}"

        hero.active = False  # делаем героя неактивным


    # Пересчитываем участников и делаем ходы монстров
    participants = battle.determine_turn_order(active_only=True)
    while participants and participants[battle.current_turn % len(participants)]['is_monster']:
        current_monster = participants[battle.current_turn % len(participants)]['entity']
        battle.monster_turn()
        current_monster.active = False
        battle.current_turn += 1  # увеличиваем ход монстра
        participants = battle.determine_turn_order(active_only=True)


    # Начало нового раунда, если все персонажи сделали ход
    if not participants:
        for hero in battle.heroes:
            hero.active = True
        for monster in battle.monsters:
            monster.active = True
        battle.current_turn = 0
        participants = battle.determine_turn_order(active_only=True)

    # Сохраняем состояние игры
    request.session['battle_state'] = battle.to_dict()

    current_participant = participants[battle.current_turn % len(participants)] if participants else None

    return render(request, 'Cards/game_play.html', {'battle': battle, 'participants': participants, 'current_participant': current_participant, 'game_over': False})