# Generated by Django 5.1.5 on 2025-01-25 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cards', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hero',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
