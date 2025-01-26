# models.py
from django.db import models


class CharacterType(models.TextChoices):
    HERO = 'HERO', 'Hero'
    MONSTER = 'MONSTER', 'Monster'


class Skill(models.Model):
    name = models.CharField(max_length=100)
    damage = models.IntegerField()

    def __str__(self):
        return self.name


class Hero(models.Model):
    name = models.CharField(max_length=100)
    health = models.IntegerField()
    attack = models.IntegerField()
    initiative = models.IntegerField()
    active = models.BooleanField(default=True)
    is_character_type = models.CharField(
        max_length=10,
        choices=CharacterType.choices,
        default=CharacterType.HERO
    )
    skills = models.ManyToManyField(Skill, blank=True)

    def __str__(self):
        return self.name


class Monster(models.Model):
    name = models.CharField(max_length=100)
    health = models.IntegerField()
    attack = models.IntegerField()
    initiative = models.IntegerField()
    active = models.BooleanField(default=True)
    is_character_type = models.CharField(
        max_length=10,
        choices=CharacterType.choices,
        default=CharacterType.MONSTER
    )
    skills = models.ManyToManyField(Skill, blank=True)

    def __str__(self):
        return self.name


class Battle(models.Model):
    battle_log = models.TextField(blank=True, default="")