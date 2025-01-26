# models.py
from django.db import models

class Skill(models.Model):
    name = models.CharField(max_length=255)
    damage = models.IntegerField()

    def __str__(self):
       return f"{self.name} ({self.damage})"

    def to_dict(self):
        return {
            'name': self.name,
            'damage': self.damage,
        }

class CharacterType(models.TextChoices):
    HERO = 'HERO', 'Hero'
    MONSTER = 'MONSTER', 'Monster'


class Card(models.Model):
    name = models.CharField(max_length=100)
    health = models.IntegerField()
    attack = models.IntegerField()
    initiative = models.IntegerField()
    active = models.BooleanField(default=True)
    skills = models.ManyToManyField(Skill, blank=True)
    is_character_type = models.CharField(max_length=10, choices=CharacterType.choices, default=CharacterType.HERO)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Hero(Card):
    def __str__(self):
       return f"<Hero: {self.name}>"


class Monster(Card):
    def __str__(self):
       return f"<Monster: {self.name}>"

