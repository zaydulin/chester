from django.contrib import admin
from .models import *


class EventsAdmin(admin.ModelAdmin):
    search_fields = ['slug', 'name']  # Enables searching by slug and name
    list_filter = ['rubrics']  # Enables filtering by rubrics

    # Other configurations for the admin panel can be added here

admin.site.register(Events, EventsAdmin)
admin.site.register(Rubrics)
admin.site.register(Team)
admin.site.register(Season)
admin.site.register(Player)
admin.site.register(Incidents)
admin.site.register(Periods)
admin.site.register(GameStatistic)
admin.site.register(H2H)
admin.site.register(TennisPoints)
admin.site.register(TennisGames)
admin.site.register(Points)
admin.site.register(PopularSeasons)