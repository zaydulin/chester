from django.contrib import admin
from .models import *


class EventsAdmin(admin.ModelAdmin):
    search_fields = ['slug', 'name','second_event_api_id']
    list_display = ['rubrics','second_event_api_id',  'start_at', 'slug', 'get_status_display', 'home_team', 'away_team',
                    'section', 'match_stream_link']
    list_filter = ['rubrics','section__country']

class IncidentsAdmin(admin.ModelAdmin):
    search_fields = ['incident_api_id']

class SeasonAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Общие настройки', {
            'fields': ['season_name','league_name', 'country', 'popular' , 'logo_league', 'season_id']
        })

    ]
    search_fields = ['slug', 'league_name']
    list_filter = ['rubrics','country']

class CountryAdmin(admin.ModelAdmin):
    list_display = ['name','name_en','image']


admin.site.register(Events, EventsAdmin)
admin.site.register(Rubrics)
admin.site.register(Stages)
admin.site.register(Team)
admin.site.register(Season,SeasonAdmin)
admin.site.register(Player)
admin.site.register(Country, CountryAdmin)
admin.site.register(Incidents,IncidentsAdmin)
admin.site.register(IncidentParticipants)
admin.site.register(Periods)
admin.site.register(GameStatistic)
admin.site.register(H2H)
admin.site.register(TennisPoints)
admin.site.register(TennisGames)
admin.site.register(Points)
admin.site.register(PopularSeasons)
