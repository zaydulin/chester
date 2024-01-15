from django.contrib import admin
from .models import *


class EventsAdmin(admin.ModelAdmin):
    search_fields = ['slug', 'name']
    list_filter = ['rubrics']

class SeasonAdmin(admin.ModelAdmin):
    search_fields = ['slug', 'name']
    list_filter = ['rubrics']

class CountryAdmin(admin.ModelAdmin):
    list_display = ['name','image']


admin.site.register(Events, EventsAdmin)
admin.site.register(Rubrics)
admin.site.register(Stages)
admin.site.register(Team)
admin.site.register(Season,SeasonAdmin)
admin.site.register(Player)
admin.site.register(Country, CountryAdmin)
admin.site.register(Incidents)
admin.site.register(IncidentParticipants)
admin.site.register(Periods)
admin.site.register(GameStatistic)
admin.site.register(H2H)
admin.site.register(TennisPoints)
admin.site.register(TennisGames)
admin.site.register(Points)
admin.site.register(PopularSeasons)
