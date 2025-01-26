from django.contrib import admin
from .models import Hero, Monster, Skill


class HeroAdmin(admin.ModelAdmin):
    filter_horizontal = ('skills',)

admin.site.register(Hero, HeroAdmin)
admin.site.register(Monster)
admin.site.register(Skill)