
from .battle_state import BattleState, CardState, SkillState
import random


class GameController:
    def __init__(self, battle):
        self.battle_state = BattleState.from_dict(battle.to_dict())
        self._participants = self.update_participants()  # _participants - свойство

    @property  # Декоратор для свойства
    def participants(self):
        return self._participants

    def update_participants(self):
        return sorted(
            [p for p in self.battle_state.heroes + self.battle_state.monsters if p.active and p.health > 0],
            key=lambda p: p.initiative, reverse=True
        )

    def get_active_participant(self):
        for p in self.participants:
            if p.active:
                return p
        return None

    def get_next_participant(self):
        active = self.get_active_participant()
        if not active:
            return None

        active.active = False
        self._participants = self.update_participants()  # обновляем _participants

        for p in self.participants:
            if p.active:
                return p
        return None

    def process_hero_turn(self, hero_id, target_id, action, skill_index=None):
        hero = next((h for h in self.battle_state.heroes if h.id == int(hero_id)), None)

        target = None
        if target_id:
            target = next((m for m in self.battle_state.monsters if m.id == int(target_id)), None)

        if action == 'attack' and target:
            damage = hero.attack
            target.health -= damage
            self.battle_state.battle_log += f"\n{hero.name} атаковал {target.name} и нанес {damage} урона."
        elif action == 'skill' and skill_index is not None and target:
            if hero.skills:
                skill = hero.skills[int(skill_index)]
                damage = skill.damage
                target.health -= damage
                self.battle_state.battle_log += f"\n{hero.name} использовал скил {skill.name} на {target.name} и нанес {damage} урона."

        self._participants = self.update_participants()  # обновляем _participants

    def process_monster_turn(self):
        active_monster = self.get_active_participant()

        if active_monster and active_monster.is_character_type == 'MONSTER':
            available_heroes = [hero for hero in self.battle_state.heroes if hero.health > 0 and hero.active]
            if available_heroes:
                target = random.choice(available_heroes)
                if active_monster.skills:
                    skill_index = random.randint(0, len(active_monster.skills) - 1)
                    skill = active_monster.skills[skill_index]
                    damage = skill.damage
                    target.health -= damage
                    self.battle_state.battle_log += f"\n{active_monster.name} использовал скил {skill.name} на {target.name} и нанес {damage} урона."
                else:
                    damage = active_monster.attack
                    target.health -= damage
                    self.battle_state.battle_log += f"\n{active_monster.name} атаковал {target.name} и нанес {damage} урона."
            active_monster.active = False
            self._participants = self.update_participants()  # обновляем _participants

    def start_new_round(self):
        for hero in self.battle_state.heroes:
            if hero.health > 0:
                hero.active = True
        for monster in self.battle_state.monsters:
            if monster.health > 0:
                monster.active = True
        self._participants = self.update_participants()  # обновляем _participants

    def is_battle_over(self):
        heroes_alive = any(hero.health > 0 for hero in self.battle_state.heroes)
        monsters_alive = any(monster.health > 0 for monster in self.battle_state.monsters)
        return not heroes_alive or not monsters_alive

    def get_battle_state(self):
        return self.battle_state.to_dict()