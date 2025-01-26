# Cards/battle_state.py
from dataclasses import dataclass, field
from typing import List, Dict
import random


@dataclass
class SkillState:
    name: str
    damage: int

    @classmethod
    def from_dict(cls, data) -> "SkillState":
        return cls(**data)


@dataclass
class CardState:
    id: int
    name: str
    health: int
    attack: int
    initiative: int
    active: bool
    is_character_type: str
    skills: List[SkillState] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data) -> "CardState":
        skills_data = data.get('skills', [])
        skills = [SkillState.from_dict(skill_data) for skill_data in skills_data]
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            health=data.get('health'),
            attack=data.get('attack'),
            initiative=data.get('initiative'),
            active=data.get('active'),
            is_character_type=data.get('is_character_type', 'HERO'),
            skills=skills
        )

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'health': self.health,
            'attack': self.attack,
            'initiative': self.initiative,
            'active': self.active,
            'is_character_type': self.is_character_type,
            'skills': [skill.__dict__ for skill in self.skills]
        }


@dataclass
class BattleState:
    participants: List[CardState] = field(default_factory=list)
    battle_log: str = ""

    @classmethod
    def from_dict(cls, data) -> "BattleState":
        heroes_data = data.get('heroes', [])
        monsters_data = data.get('monsters', [])
        participants = [CardState.from_dict(hero_data) for hero_data in heroes_data] + [
            CardState.from_dict(monster_data) for monster_data in monsters_data]
        return cls(
            participants=participants,
            battle_log=data.get('battle_log', '')
        )

    def to_dict(self) -> Dict:
        return {
            'heroes': [p.to_dict() for p in self.participants if p.is_character_type == 'HERO'],
            'monsters': [p.to_dict() for p in self.participants if p.is_character_type == 'MONSTER'],
            'battle_log': self.battle_log,
        }

    def update_participants(self):
        self.participants = sorted(
            [p for p in self.participants if p.active and p.health > 0],
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
        self.update_participants()

        for p in self.participants:
            if p.active:
                return p
        return None

    def process_hero_turn(self, hero_id, target_id, action, skill_index=None):
        hero = next((h for h in self.participants if h.id == int(hero_id)), None)
        target = None
        if target_id:
            target = next((m for m in self.participants if m.id == int(target_id)), None)

        if action == 'attack' and target:
            damage = hero.attack
            target.health -= damage
            self.battle_log += f"\n{hero.name} атаковал {target.name} и нанес {damage} урона."
        elif action == 'skill' and skill_index is not None and target:
            if hero.skills:
                skill = hero.skills[int(skill_index)]
                damage = skill.damage
                target.health -= damage
                self.battle_log += f"\n{hero.name} использовал скил {skill.name} на {target.name} и нанес {damage} урона."

        self.update_participants()

    def process_monster_turn(self):
        active_monster = self.get_active_participant()

        if active_monster and active_monster.is_character_type == 'MONSTER':
            available_heroes = [hero for hero in self.participants if
                                hero.health > 0 and hero.active and hero.is_character_type == 'HERO']
            if available_heroes:
                target = random.choice(available_heroes)
                if active_monster.skills:
                    skill_index = random.randint(0, len(active_monster.skills) - 1)
                    skill = active_monster.skills[skill_index]
                    damage = skill.damage
                    target.health -= damage
                    self.battle_log += f"\n{active_monster.name} использовал скил {skill.name} на {target.name} и нанес {damage} урона."
                else:
                    damage = active_monster.attack
                    target.health -= damage
                    self.battle_log += f"\n{active_monster.name} атаковал {target.name} и нанес {damage} урона."
            self.update_participants()

    def start_new_round(self):
        for p in self.participants:
            if p.health > 0:
                p.active = True
        self.update_participants()

    def is_battle_over(self):
        heroes_alive = any(p.health > 0 for p in self.participants if p.is_character_type == 'HERO')
        monsters_alive = any(p.health > 0 for p in self.participants if p.is_character_type == 'MONSTER')
        return not heroes_alive or not monsters_alive
