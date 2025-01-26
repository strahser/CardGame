# Generated by Django 5.1.5 on 2025-01-26 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cards', '0004_monster_skills'),
    ]

    operations = [
        migrations.AddField(
            model_name='hero',
            name='is_character_type',
            field=models.CharField(choices=[('HERO', 'Hero'), ('MONSTER', 'Monster')], default='HERO', max_length=10),
        ),
        migrations.AddField(
            model_name='monster',
            name='is_character_type',
            field=models.CharField(choices=[('HERO', 'Hero'), ('MONSTER', 'Monster')], default='HERO', max_length=10),
        ),
    ]
