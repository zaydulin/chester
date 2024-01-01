from itertools import groupby

from django import template
from django.conf import settings
from events.models import Rubrics, PopularSeasons, Season
from events.forms import EventSearchForm

register = template.Library()


@register.simple_tag()
def get_first_rubric():
    try:
        return Rubrics.objects.get(sortable=1)
    except Rubrics.DoesNotExist:
        return None


@register.simple_tag()
def get_rubric_max_six():
    excluded_sortable = [7]
    return Rubrics.objects.exclude(sortable__in=excluded_sortable).order_by("sortable")[:6]


@register.simple_tag()
def get_rubric_three():
    excluded_ids = [1, 2, 3]
    return Rubrics.objects.exclude(sortable__in=excluded_ids).order_by("sortable")


@register.simple_tag()
def get_rubric_six():
    excluded_ids = [1, 2, 3, 4, 5, 6]
    return Rubrics.objects.exclude(sortable__in=excluded_ids).order_by("sortable")


@register.inclusion_tag("event_search_form.html")
def event_search_form():
    form = EventSearchForm()
    return {"form": form}


@register.simple_tag()
def get_popular_seasons():
    return PopularSeasons.objects.all().order_by("position")[:10]


@register.simple_tag()
def get_country_seasons(request):
    url = request.path
    if url.startswith("football/") :
        rubric_id = 1
    elif url.startswith("volleyball/"):
        rubric_id = 12
    elif url.startswith("hockey/"):
        rubric_id = 4
    elif url.startswith("basketball/") :
        rubric_id = 3
    elif url.startswith("tennis/") :
        rubric_id = 2
    elif url.startswith("handball/") :
        rubric_id = 7
    elif url.startswith("cybersport/") :
        rubric_id = 36
    elif url.startswith("baseball/") :
        rubric_id = 6
    elif url.startswith("cricket/") :
        rubric_id = 13
    elif url.startswith("snooker/") :
        rubric_id = 15
    elif url.startswith("table-tennis/") :
        rubric_id = 25
    elif url.startswith("badminton/"):
        rubric_id = 21
    else:
        rubric_id = 1

    seasons = Season.objects.filter(country__isnull=False,rubrics__api_id=rubric_id).order_by("country")

    grouped_seasons = {}
    for country, season_group in groupby(seasons, key=lambda season: season.country):
        grouped_seasons[country] = list(season_group)

    return grouped_seasons


@register.simple_tag()
def get_context(request):
    url = request.path
    if url.endswith("upcoming/"):
        return "upcoming"
    elif url.endswith("end/"):
        return "end"
    elif url.endswith("football/") or url.endswith("volleyball/") or url.endswith("hockey/") or url.endswith("basketball/") or url.endswith("tennis/") or url.endswith("handball/") or url.endswith("cybersport/") or url.endswith("baseball/") or url.endswith("cricket/") or url.endswith("snooker/") or url.endswith("table-tennis/") or url.endswith("table-tennis/") or url.endswith("badminton/") :
        return "now"
    else:
        return None



@register.simple_tag
def check_sport_rubric(request):
    rubrics = Rubrics.objects.all()
    url = request.path
    for rubric in rubrics:
        if url.startswith(f"/{rubric.slug}/"):
            rubricactive = rubric.slug
            request.session["rubric_active"] = ""
            request.session["rubric_active"] = rubricactive
            return rubricactive
        else:
            request.session["rubric_active"] = "football"


@register.simple_tag
def get_settings(name):
    return getattr(settings, name, "")
