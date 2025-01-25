# models.py
from django.db import models
import random


class Card(models.Model):
    name = models.CharField(max_length=100)
    health = models.IntegerField()
    attack = models.IntegerField()
    initiative = models.IntegerField()
    active = models.BooleanField(default=True)  # Добавляем поле active

    class Meta:
        abstract = True  # базовая модель, от нее наследуемся

    def __str__(self):
        return self.name

    def to_dict(self):
        """Конвертирует объект в словарь."""
        return {
            'id': self.id,
            'name': self.name,
            'health': self.health,
            'attack': self.attack,
            'initiative': self.initiative,
            'active': self.active,
            **self.extra_data_to_dict()  # добавляем дополнительные данные
        }

    @classmethod
    def from_dict(cls, data):
        """Создает объект из словаря."""
        obj = cls()
        obj.id = data.get('id')  # можем и не передавать id
        obj.name = data['name']
        obj.health = data['health']
        obj.attack = data['attack']
        obj.initiative = data['initiative']
        obj.active = data.get('active', True)  # устанавливаем active из словаря или true по умолчанию
        obj = cls.set_extra_data_from_dict(obj, data)
        return obj

    def extra_data_to_dict(self):
        """Дополнительные данные для дочерних классов"""
        return {}

    @classmethod
    def set_extra_data_from_dict(cls, obj, data):
        """Устанавливаем доп данные из словаря"""
        return obj


class Hero(Card):
    skills = models.JSONField(default=list, blank=True)  # список скиллов. пока пустой.

    def use_skill(self, skill_index, target):
        """Применяет скилл. пока в зачаточном состоянии"""
        if skill_index < len(self.skills):
            skill = self.skills[skill_index]
            damage = skill.get('damage', 0)
            target.health -= damage
            return f"{self.name} применил скилл {skill['name']} на {target.name} и нанес {damage} урона."
        return None

    def normal_attack(self, target):
        target.health -= self.attack
        return f"{self.name} атаковал {target.name} и нанес {self.attack} урона."

    def extra_data_to_dict(self):
        """дополнительные данные для героя"""
        return {'skills': self.skills}

    @classmethod
    def set_extra_data_from_dict(cls, obj, data):
        """Устанавливаем доп данные из словаря"""
        obj.skills = data['skills']
        return obj


class Monster(Card):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_monster = True  # для удобства, чтобы отличать от героя


class Battle:  # больше не models.Model
    def __init__(self):
        self.heroes = []  # теперь это список объектов
        self.monsters = []  # теперь это список объектов
        self.current_turn = 0
        self.battle_log = ""

    def get_participants(self):
        """Объединяет героев и монстров в список с инициативой для определения порядка хода."""
        participants = []
        for hero in self.heroes:
            participants.append({"entity": hero, "initiative": hero.initiative, 'is_monster': False})
        for monster in self.monsters:
            participants.append({"entity": monster, "initiative": monster.initiative, 'is_monster': True})
        return participants

    def get_active_participants(self):
        """Получает только активных персонажей."""
        participants = []
        for hero in self.heroes:
            if hero.active:
                participants.append({"entity": hero, "initiative": hero.initiative, 'is_monster': False})
        for monster in self.monsters:
            if monster.active:
                participants.append({"entity": monster, "initiative": monster.initiative, 'is_monster': True})
        return participants

    def determine_turn_order(self, active_only=True):
        """Определяет порядок хода на основе инициативы.
        Если active_only=True - то только для активных.  Добавляет tie-breaker по ID."""
        participants = self.get_active_participants() if active_only else self.get_participants()
        participants.sort(key=lambda x: (x['initiative'], -x['entity'].id), reverse=True) # tie-breaker по ID
        return participants

    def battle_over(self):
        """Проверка окончания боя. Возвращает True, если бой закончен, иначе False"""
        all_heroes_dead = all(hero.health <= 0 for hero in self.heroes)
        all_monsters_dead = all(monster.health <= 0 for monster in self.monsters)

        if all_heroes_dead:
            self.battle_log += "\nВсе герои мертвы. Вы проиграли!"
            return True

        if all_monsters_dead:
            self.battle_log += "\nВсе монстры побеждены. Вы выиграли!"
            return True

        return False

    def monster_turn(self):
        """Ход монстра. Монстр выбирает случайную цель (живого героя) и атакует ее."""
        participants = self.determine_turn_order(active_only=True)

        if not participants:  # если нет активных - начинаем новый круг
            for hero in self.heroes:  # делаем всех героев активными
                hero.active = True
            for monster in self.monsters:
                monster.active = True
            self.current_turn = 0
            participants = self.determine_turn_order(active_only=True)  # пересчитываем список
            return ""  # ни чего не делаем

        current_participant = participants[self.current_turn % len(participants)]

        if current_participant['is_monster'] and current_participant['entity'].health > 0:  # убрали проверку active
            monster = current_participant['entity']
            available_heroes = [hero for hero in self.heroes if hero.health > 0 and hero.active]
            if available_heroes:
                target = random.choice(available_heroes)
                damage = monster.attack
                self.battle_log += f"\n{monster.name} атакует {target.name} и наносит {damage} урона."

            monster.active = False  # делаем монстра не активным

        return self.battle_log


    def to_dict(self):
        """Конвертирует объект Battle в словарь."""
        return {
            'heroes': [hero.to_dict() for hero in self.heroes],
            'monsters': [monster.to_dict() for monster in self.monsters],
            'current_turn': self.current_turn,
            'battle_log': self.battle_log,
        }

    @classmethod
    def from_dict(cls, data):
        """Создает объект Battle из словаря."""
        battle = cls()
        battle.heroes = [Hero.from_dict(h) for h in data['heroes']]
        battle.monsters = [Monster.from_dict(m) for m in data['monsters']]
        battle.current_turn = data['current_turn']
        battle.battle_log = data['battle_log']
        return battle