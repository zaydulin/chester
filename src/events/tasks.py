from celery import shared_task
import requests
from datetime import datetime
from .models import Rubrics, Season, Team, Events, H2H, Country
from django.db.models import Q
from events.models import Rubrics, Events, Team, Season, Player, Incidents, Periods, GameStatistic, H2H, TennisPoints, \
    TennisGames, Points , Country,Stages



HEADER_FOR_FIRST_API = {
        "X-RapidAPI-Key": "3b1726a15fmshc58a145e91a5846p197521jsn5a6af790e789",
        "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
}

HEADER_FOR_SECOND_API = {
    "X-RapidAPI-Key": "11047ab519mshed06c5cc71509fep168f75jsn077ef01d5d10",
    "X-RapidAPI-Host": "flashlive-sports.p.rapidapi.com"
}
HEADER_FOR_SECOND_API_GOU = {
    "X-RapidAPI-Key": "11047ab519mshed06c5cc71509fep168f75jsn077ef01d5d10",
    "X-RapidAPI-Host": "flashlive-sports.p.rapidapi.com"
}

def get_unique_season_slug(base_slug):
    try:
        existing_season = Season.objects.get(slug=base_slug)

        slug_suffix = 1
        while True:
            new_slug = f"{base_slug}-{slug_suffix}"
            if not Season.objects.filter(slug=new_slug).exists():
                break
            slug_suffix += 1

        return new_slug
    except Season.DoesNotExist:
        return base_slug
# Вторая апи
@shared_task
def create_tournament():
    tournaments_list_url = "https://flashlive-sports.p.rapidapi.com/v1/tournaments/list"
    second_api_rubric_ids = Rubrics.objects.filter(second_api=True).values_list("api_id", flat=True).distinct()

    for rubric_id in [1,2,3,4,12,7,36,6,15,13,25,21]:
        rubric_id_q = str(rubric_id)
        querystring_tournaments_list = {"sport_id": rubric_id_q, "locale": "ru_RU"}
        rubrics = Rubrics.objects.get(second_api=True, api_id=rubric_id)
        response_tournaments_list = requests.get(tournaments_list_url, headers=HEADER_FOR_SECOND_API,params=querystring_tournaments_list)
        if response_tournaments_list.status_code == 200:
            tournaments_data = response_tournaments_list.json()
            for tournament_data in tournaments_data.get("DATA", []):
                country_name = tournament_data.get('COUNTRY_NAME')
                if Country.objects.filter(name=country_name).exists():
                    country = Country.objects.get(name=country_name)
                else:
                    country = Country.objects.create(name=country_name)
                season_id = tournament_data.get("ACTUAL_TOURNAMENT_SEASON_ID")
                try:
                    season = Season.objects.get(
                        rubrics=rubrics,
                        season_id=season_id,
                    )
                except:
                    season = Season.objects.create(
                        rubrics=rubrics,
                        league_name=tournament_data.get("LEAGUE_NAME"),
                        season_id=season_id,
                        country = country
                    )
                stages = tournament_data.get("STAGES")
                for stage in stages:
                    stage_id = stage.get("STAGE_ID")
                    stage_name = stage.get("STAGE_NAME")
                    try :
                        stage_bd = Stages.objects.create(stage_id=stage_id)
                    except:
                        stage_bd = Stages.objects.create(stage_id=stage_id,stage_name=stage_name)
                    season.stages.add(stage_bd)
        else:
            return {"response": f"Error  - {response_tournaments_list.status_code} - {response_tournaments_list.json()}"}

    return {"response": "create_tournament successfully"}

@shared_task
def create_events_of_tournament():
    second_url = "https://flashlive-sports.p.rapidapi.com/v1/tournaments/fixtures"
    second_api_rubric_ids = Rubrics.objects.filter(second_api=True).values_list("api_id", flat=True).distinct()
    for rubric_id in [1,2,3,4,12,7,36,6,15,13,25,21]:
        seasons = Season.objects.filter(rubrics__api_id=rubric_id)
        for season in seasons:
            stages = season.stages.all()
            for stage in stages:
                querystring = {"locale": "ru_RU", "tournament_stage_id": str(stage.stage_id), "page": "1"}
                rubrics = Rubrics.objects.get(second_api=True, api_id=rubric_id)
                second_response = requests.get(second_url, headers=HEADER_FOR_SECOND_API, params=querystring)
                if second_response.status_code == 200:
                    response_data = second_response.json()
                    for event_data in response_data.get("DATA", []):
                        # Создайте записи для команд (Team)
                        events = event_data.get("EVENTS")
                        logo_season = event_data.get("TOURNAMENT_IMAGE")
                        if logo_season:
                            correct_logo_season = logo_season.replace('www.', 'static.')
                        else:
                            correct_logo_season = ''
                        try:
                            season = Season.objects.get(
                                rubrics=rubrics, season_id=event_data.get("TOURNAMENT_SEASON_ID")
                            )
                            season.logo_league = correct_logo_season
                            season.season_name = event_data.get("NAME")
                            season.season_second_api_id = event_data.get("TOURNAMENT_STAGE_ID")
                            season.save()
                        except:
                            country_from_db, created = Country.objects.get_or_create(
                                name=event_data.get("COUNTRY_NAME"))
                            season = Season.objects.create(
                                rubrics=rubrics,
                                season_second_api_id=event_data.get("TOURNAMENT_STAGE_ID"),
                                season_name=event_data.get("NAME"),
                                logo_league=correct_logo_season,
                                league_name=event_data.get("NAME"),
                                season_id=event_data.get("TOURNAMENT_SEASON_ID"),
                                country=country_from_db,
                            )
                        for event in events:
                            homeimg_base = event.get("HOME_IMAGES")
                            awayimg_base = event.get("AWAY_IMAGES")
                            status = event.get("STAGE_TYPE")
                            if status == 'SCHEDULED':
                                status_id = 3
                            elif status == 'LIVE':
                                status_id = 1
                            elif status == 'FINISHED':
                                status_id = 2
                            if homeimg_base is not None and awayimg_base is not None:
                                logo_home = event.get("HOME_IMAGES")[-1]
                                if logo_home:
                                    correct_home_logo = logo_home.replace('www.', 'static.')
                                else:
                                    correct_home_logo = ''
                                logo_away = event.get("AWAY_IMAGES")[-1]
                                if logo_away:
                                    correct_away_logo = logo_away.replace('www.', 'static.')
                                else:
                                    correct_away_logo = ''
                                try:
                                    home_team = Team.objects.get(
                                        second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1])
                                except:

                                    home_team = Team.objects.create(
                                        second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1],
                                        name=event.get("HOME_NAME"),
                                        logo=correct_home_logo,
                                        rubrics=rubrics,
                                    )
                                try:
                                    away_team = Team.objects.get(
                                        second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1])
                                except:
                                    away_team = Team.objects.create(
                                        second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1],
                                        name=event.get("AWAY_NAME"),
                                        logo=correct_away_logo,
                                        rubrics=rubrics,
                                    )
                                if not Events.objects.filter(
                                        rubrics=rubrics, second_event_api_id=event.get("EVENT_ID")
                                ).exists():
                                    Events.objects.create(
                                        rubrics=rubrics,
                                        second_event_api_id=event.get("EVENT_ID"),
                                        start_at=datetime.utcfromtimestamp(event.get("START_TIME")),
                                        name=event_data.get("NAME_PART_2"),
                                        description=event_data,
                                        title=event_data.get("SHORT_NAME"),
                                        status=status_id,
                                        home_team=home_team,
                                        away_team=away_team,
                                        home_score=event.get("HOME_SCORE_CURRENT"),
                                        away_score=event.get("AWAY_SCORE_CURRENT"),
                                        half=event.get("ROUND"),
                                        section=season,
                                    )
                elif second_response.status_code == 404:
                    try:
                        stage.delete()
                    except:
                        pass
                    try:
                        season.delete()
                    except:
                        pass
                else:
                    #         return HttpResponse(f"Error  - {second_response.status_code} - {second_response.json()}")
                    # return HttpResponse("Data fetched successfully")
                    return {"response": f"Error  - {second_response.status_code} - {second_response.json()}"}
    return {"response": "create_events_of_tournament successfully"}
@shared_task
def fetch_event_data_for_second():
    events = Events.objects.filter(~Q(status=2),second_event_api_id__isnull=False)
    url = "https://flashlive-sports.p.rapidapi.com/v1/events/data"
    for event in events:
        querystring = {"locale": "en_INT", "event_id": event.second_event_api_id}
        response = requests.get(url, headers=HEADER_FOR_SECOND_API, params=querystring)
        if response.status_code == 200:
            response_data = response.json().get("DATA").get("EVENT")
            hsc = response_data.get("HOME_SCORE_CURRENT")
            asc = response_data.get("AWAY_SCORE_CURRENT")
            status = response_data.get("STAGE_TYPE")
            event.home_score = hsc
            event.away_score = asc
            if status == "FINISHED":
                event.status = 2
            event.save()
        # second_url = "https://flashlive-sports.p.rapidapi.com/v1/events/h2h"
        #
        # second_querystring = {"locale": "en_INT", "event_id": event.second_event_api_id}
        #
        # second_response = requests.get(second_url, headers=HEADER_FOR_SECOND_API, params=second_querystring)
        # if second_response.status_code == 200:
        #     second_response_data = second_response.json().get("DATA", [])
        #     for el in second_response_data:
        #         groups = el.get("GROUPS")
        #         for group in groups:
        #             items = group.get("ITEMS", [])
        #             for item in items:
        #                 hi = item.get("HOME_IMAGES")
        #                 ai = item.get("AWAY_IMAGES")
        #                 if hi is not None and ai is not None:
        #                     if not H2H.objects.filter(
        #                         home_score=item.get("HOME_SCORE_FULL"),
        #                         away_score=item.get("AWAY_SCORE_FULL"),
        #                         name=item.get("EVENT_NAME"),
        #                         home_team_NAME=item.get("HOME_PARTICIPANT"),
        #                         home_team_LOGO=item.get("HOME_IMAGES")[-1],
        #                         away_team_NAME=item.get("AWAY_PARTICIPANT"),
        #                         away_team_LOGO=item.get("AWAY_IMAGES")[-1],
        #                         league=item.get("EVENT_NAME"),
        #                         start_at=datetime.utcfromtimestamp(item.get("START_TIME")),
        #                         h_result=item.get("H_RESULT"),
        #                         team_mark=item.get("TEAM_MARK"),
        #                     ).exists():
        #                         h2h = H2H.objects.create(
        #                             home_score=item.get("HOME_SCORE_FULL"),
        #                             away_score=item.get("AWAY_SCORE_FULL"),
        #                             name=item.get("EVENT_NAME"),
        #                             home_team_NAME=item.get("HOME_PARTICIPANT"),
        #                             home_team_LOGO=item.get("HOME_IMAGES")[-1],
        #                             away_team_NAME=item.get("AWAY_PARTICIPANT"),
        #                             away_team_LOGO=item.get("AWAY_IMAGES")[-1],
        #                             league=item.get("EVENT_NAME"),
        #                             start_at=datetime.utcfromtimestamp(item.get("START_TIME")),
        #                             h_result=item.get("H_RESULT"),
        #                             team_mark=item.get("TEAM_MARK"),
        #                         )
        #                         event.h2h.add(h2h)
        #                         event.save()
        #                     else:
        #                         h2h = H2H.objects.filter(
        #                         home_score=item.get("HOME_SCORE_FULL"),
        #                         away_score=item.get("AWAY_SCORE_FULL"),
        #                         name=item.get("EVENT_NAME"),
        #                         home_team_NAME=item.get("HOME_PARTICIPANT"),
        #                         home_team_LOGO=item.get("HOME_IMAGES")[-1],
        #                         away_team_NAME=item.get("AWAY_PARTICIPANT"),
        #                         away_team_LOGO=item.get("AWAY_IMAGES")[-1],
        #                         league=item.get("EVENT_NAME"),
        #                         start_at=datetime.utcfromtimestamp(item.get("START_TIME")),
        #                         h_result=item.get("H_RESULT"),
        #                         team_mark=item.get("TEAM_MARK"),
        #                         ).first()
        #                         event.h2h.add(h2h)
        #                         event.save()
    return {"response": "fetch_event_data_for_second successfully"}
    # return HttpResponse("Data fetched successfully")

# @shared_task
# def add_sport_events_list_second():
#     second_url = "https://flashlive-sports.p.rapidapi.com/v1/events/list"
#
#     second_api_rubric_ids = Rubrics.objects.filter(second_api=True).values_list("api_id", flat=True).distinct()
#
#     for rubric_id in second_api_rubric_ids:
#         rubric_id_q = str(rubric_id)
#         querystring = {"timezone": "-4", "indent_days": "-7", "locale": "ru_RU", "sport_id": rubric_id_q}
#         rubrics = Rubrics.objects.get(second_api=True, api_id=rubric_id)
#         second_response = requests.get(second_url, headers=HEADER_FOR_SECOND_API, params=querystring)
#         if second_response.status_code == 200:
#             response_data = second_response.json()
#             for event_data in response_data.get("DATA", []):
#                 # Создайте записи для команд (Team)
#                 events = event_data.get("EVENTS")
#                 logo_season = event_data.get("TOURNAMENT_IMAGE")
#                 if logo_season:
#                     correct_logo_season = logo_season.replace('www.','static.')
#                 else:
#                     correct_logo_season = ''
#                 try:
#                     season = Season.objects.get(
#                         rubrics=rubrics, season_second_api_id=event_data.get("TOURNAMENT_SEASON_ID")
#                     )
#                 except:
#                     country_from_db, created = Country.objects.get_or_create(name=event_data.get("COUNTRY_NAME"))
#                     season = Season.objects.create(
#                         rubrics=rubrics,
#                         season_second_api_id=event_data.get("TOURNAMENT_SEASON_ID"),
#                         season_name=event_data.get("NAME"),
#                         logo_league=correct_logo_season,
#                         country=country_from_db,
#                     )
#                 for event in events:
#                     homeimg_base = event.get("HOME_IMAGES")
#                     awayimg_base = event.get("AWAY_IMAGES")
#                     status = event.get("STAGE_TYPE")
#                     if status == 'SCHEDULED':
#                         status_id = 3
#                     elif status == 'LIVE':
#                         status_id = 1
#                     elif status == 'FINISHED':
#                         status_id = 2
#                     if homeimg_base is not None and awayimg_base is not None:
#                         logo_home = event.get("HOME_IMAGES")[-1]
#                         if logo_home:
#                             correct_home_logo = logo_home.replace('www.', 'static.')
#                         else:
#                             correct_home_logo = ''
#                         logo_away = event.get("AWAY_IMAGES")[-1]
#                         if logo_away:
#                             correct_away_logo = logo_away.replace('www.', 'static.')
#                         else:
#                             correct_away_logo = ''
#                         try:
#                             home_team = Team.objects.get(second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1])
#                         except:
#
#                             home_team = Team.objects.create(
#                                 second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1],
#                                 name=event.get("HOME_NAME"),
#                                 logo=correct_home_logo,
#                                 rubrics=rubrics,
#                             )
#                         try:
#                             away_team = Team.objects.get(second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1])
#                         except:
#                             away_team = Team.objects.create(
#                                 second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1],
#                                 name=event.get("AWAY_NAME"),
#                                 logo=correct_away_logo,
#                                 rubrics=rubrics,
#                             )
#                         if not Events.objects.filter(
#                             rubrics=rubrics, second_event_api_id=event.get("EVENT_ID")
#                         ).exists():
#                             Events.objects.create(
#                                 rubrics=rubrics,
#                                 second_event_api_id=event.get("EVENT_ID"),
#                                 start_at=datetime.utcfromtimestamp(event.get("START_TIME")),
#                                 name=event_data.get("NAME_PART_2"),
#                                 description=event_data,
#                                 title=event_data.get("SHORT_NAME"),
#                                 status=status_id,
#                                 home_team=home_team,
#                                 away_team=away_team,
#                                 home_score=event.get("HOME_SCORE_CURRENT"),
#                                 away_score=event.get("AWAY_SCORE_CURRENT"),
#                                 half=event.get("ROUND"),
#                                 section=season,
#                             )
#         else:
#     #         return HttpResponse(f"Error  - {second_response.status_code} - {second_response.json()}")
#     # return HttpResponse("Data fetched successfully")
#             return {"response": f"Error  - {second_response.status_code} - {second_response.json()}"}
#         return {"response": "add_sport_events_list_second successfully"}
#
# @shared_task
# def add_sport_events_list_second_future():
#     second_url = "https://flashlive-sports.p.rapidapi.com/v1/events/list"
#
#     second_api_rubric_ids = Rubrics.objects.filter(second_api=True).values_list("api_id", flat=True).distinct()
#
#     for rubric_id in second_api_rubric_ids:
#         rubric_id_q = str(rubric_id)
#         querystring = {"timezone": "-4", "indent_days": "7", "locale": "ru_RU", "sport_id": rubric_id_q}
#         rubrics = Rubrics.objects.get(second_api=True, api_id=rubric_id)
#         second_response = requests.get(second_url, headers=HEADER_FOR_SECOND_API, params=querystring)
#         if second_response.status_code == 200:
#             response_data = second_response.json()
#             for event_data in response_data.get("DATA", []):
#                 # Создайте записи для команд (Team)
#                 events = event_data.get("EVENTS")
#                 logo_season = event_data.get("TOURNAMENT_IMAGE")
#                 if logo_season:
#                     correct_logo_season = logo_season.replace('www.','static.')
#                 else:
#                     correct_logo_season = ''
#                 try:
#                     season = Season.objects.get(
#                         rubrics=rubrics, season_second_api_id=event_data.get("TOURNAMENT_SEASON_ID")
#                     )
#                 except:
#                     country_from_db, created = Country.objects.get_or_create(name=event_data.get("COUNTRY_NAME"))
#                     season = Season.objects.create(
#                         rubrics=rubrics,
#                         season_second_api_id=event_data.get("TOURNAMENT_SEASON_ID"),
#                         season_name=event_data.get("NAME"),
#                         logo_league=correct_logo_season,
#                         country=country_from_db,
#                     )
#                 for event in events:
#                     homeimg_base = event.get("HOME_IMAGES")
#                     awayimg_base = event.get("AWAY_IMAGES")
#                     status = event.get("STAGE_TYPE")
#                     if status == 'SCHEDULED':
#                         status_id = 3
#                     elif status == 'LIVE':
#                         status_id = 1
#                     elif status == 'FINISHED':
#                         status_id = 2
#                     if homeimg_base is not None and awayimg_base is not None:
#                         logo_home = event.get("HOME_IMAGES")[-1]
#                         if logo_home:
#                             correct_home_logo = logo_home.replace('www.','static.')
#                         else :
#                             correct_home_logo = ''
#                         logo_away = event.get("AWAY_IMAGES")[-1]
#                         if logo_away:
#                             correct_away_logo = logo_away.replace('www.', 'static.')
#                         else :
#                             correct_away_logo = ''
#                         try:
#                             home_team = Team.objects.get(second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1])
#                         except:
#
#                             home_team = Team.objects.create(
#                                 second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1],
#                                 name=event.get("HOME_NAME"),
#                                 logo=correct_home_logo,
#                                 rubrics=rubrics,
#                             )
#                         try:
#                             away_team = Team.objects.get(second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1])
#                         except:
#                             away_team = Team.objects.create(
#                                 second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1],
#                                 name=event.get("AWAY_NAME"),
#                                 logo=correct_away_logo,
#                                 rubrics=rubrics,
#                             )
#                         if not Events.objects.filter(
#                             rubrics=rubrics, second_event_api_id=event.get("EVENT_ID")
#                         ).exists():
#                             Events.objects.create(
#                                 rubrics=rubrics,
#                                 second_event_api_id=event.get("EVENT_ID"),
#                                 start_at=datetime.utcfromtimestamp(event.get("START_TIME")),
#                                 name=event_data.get("NAME_PART_2"),
#                                 description=event_data,
#                                 title=event_data.get("SHORT_NAME"),
#                                 status=status_id,
#                                 home_team=home_team,
#                                 away_team=away_team,
#                                 home_score=event.get("HOME_SCORE_CURRENT"),
#                                 away_score=event.get("AWAY_SCORE_CURRENT"),
#                                 half=event.get("ROUND"),
#                                 section=season,
#                             )
#         else:
#     #         return HttpResponse(f"Error  - {second_response.status_code} - {second_response.json()}")
#     # return HttpResponse("Data fetched successfully")
#             return {"response": f"Error  - {second_response.status_code} - {second_response.json()}"}
#         return {"response": "add_sport_events_list_second_future successfully"}
#
# @shared_task
# def add_sport_events_list_second_online_gou():
#     second_url = "https://flashlive-sports.p.rapidapi.com/v1/events/live-list"
#
#     second_api_rubric_ids = Rubrics.objects.filter(second_api=True).values_list("api_id", flat=True).distinct()
#
#     for rubric_id in second_api_rubric_ids:
#         rubric_id_q = str(rubric_id)
#         querystring = {"timezone": "-4","sport_id": rubric_id_q, "locale": "ru_RU" }
#         rubrics = Rubrics.objects.get(second_api=True, api_id=rubric_id)
#         second_response = requests.get(second_url, headers=HEADER_FOR_SECOND_API_GOU, params=querystring)
#         if second_response.status_code == 200:
#             response_data = second_response.json()
#             for event_data in response_data.get("DATA", []):
#                 events = event_data.get("EVENTS")
#                 logo_season = event_data.get("TOURNAMENT_IMAGE")
#
#                 if logo_season:
#                     correct_logo_season = logo_season.replace('www.', 'static.')
#                 else:
#                     correct_logo_season = ''
#                 try:
#                     season_sountry = Country.objects.get(name=event_data.get("COUNTRY_NAME"))
#                 except:
#                     season_sountry = Country.objects.create(name=event_data.get("COUNTRY_NAME"))
#                 try:
#                     season = Season.objects.get(
#                         rubrics=rubrics, season_second_api_id=event_data.get("TOURNAMENT_SEASON_ID")
#                     )
#                 except Season.DoesNotExist:
#                     season = Season.objects.create(
#                         rubrics=rubrics,
#                         season_second_api_id=event_data.get("TOURNAMENT_SEASON_ID"),
#                         season_name=event_data.get("NAME"),
#                         logo_league=correct_logo_season,
#                         country=season_sountry,
#                     )
#                 for event in events:
#                     homeimg_base = event.get("HOME_IMAGES")
#                     awayimg_base = event.get("AWAY_IMAGES")
#                     if homeimg_base is not None and awayimg_base is not None:
#                         logo_home = event.get("HOME_IMAGES")[-1]
#                         if logo_home:
#                             correct_home_logo = logo_home.replace('www.', 'static.')
#                         else:
#                             correct_home_logo = ''
#                         logo_away = event.get("AWAY_IMAGES")[-1]
#                         if logo_away:
#                             correct_away_logo = logo_away.replace('www.', 'static.')
#                         else:
#                             correct_away_logo = ''
#                         if Team.objects.filter(second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1]).exists():
#                             home_team = Team.objects.get(second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1])
#                         else:
#                             home_team = Team.objects.create(
#                                 second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1],
#                                 name=event.get("HOME_NAME"),
#                                 logo=correct_home_logo,
#                                 rubrics=rubrics,
#                             )
#                         if Team.objects.filter(second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1]).exists():
#                             away_team = Team.objects.get(second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1])
#                         else:
#                             away_team = Team.objects.create(
#                                 second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1],
#                                 name=event.get("AWAY_NAME"),
#                                 logo=correct_away_logo,
#                                 rubrics=rubrics,
#                             )
#
#                         if not Events.objects.filter(
#                                 rubrics=rubrics,
#                                 second_event_api_id=event.get("EVENT_ID"),
#                         ).exists():
#                             Events.objects.create(
#                                 rubrics=rubrics,
#                                 second_event_api_id=event.get("EVENT_ID"),
#                                 start_at=datetime.utcfromtimestamp(event.get("START_TIME")),
#                                 name=event_data.get("NAME_PART_2"),
#                                 description=event_data,
#                                 title=event_data.get("SHORT_NAME"),
#                                 status=1,
#                                 home_team=home_team,
#                                 away_team=away_team,
#                                 home_score=event.get("HOME_SCORE_CURRENT"),
#                                 away_score=event.get("AWAY_SCORE_CURRENT"),
#                                 half=event.get("ROUND"),
#                                 section=season,
#                             )
#         else:
#             return {"response": f"Error  - {second_response.status_code} - {second_response.json()}"}
#     return {"response": "add_sport_events_list_second_online_gou successfully"}



# @shared_task
# def get_team_players_second():
#     url = "https://flashlive-sports.p.rapidapi.com/v1/events/lineups"
#     events = Events.objects.filter(second_event_api_id__isnull = False ,status=1)
#     for event in events:
#         querystring = {"locale": "ru_RU", "event_id": event.second_event_api_id}
#         response = requests.get(url, headers=HEADER_FOR_SECOND_API, params=querystring)
#         if response.status_code == 200:
#             response_data = response.json().get("DATA")
#             for data in response_data:
#                 formation_name = data.get("FORMATION_NAME")
#                 formations = data.get("FORMATIONS",[])
#                 for formation in formations:
#                     team_line = formation.get("FORMATION_LINE")
#                     members = formation.get("MEMBERS",[])
#                     for player in members:
#                         try:
#                             player = Player.objects.get(player_id=player["id"])
#                         except Player.DoesNotExist:
#                             if team_line == 1:
#                                 if formation_name == 'Starting Lineups':
#                                     player = Player.objects.create(
#                                         player_id=player["PLAYER_ID"],
#                                         slug=f'{player["PLAYER_FULL_NAME"]} + {player["PLAYER_ID"]}',
#                                         name=player["PLAYER_FULL_NAME"],
#                                         photo=f'https://www.flashscore.com/res/image/data/{player["LPI"]}',
#                                         position_name=player["PLAYER_POSITION"],
#                                         description=player,
#                                         main_player=True,
#                                         number=player["PLAYER_NUMBER"],
#                                     )
#                                 else :
#                                     player = Player.objects.create(
#                                         player_id=player["PLAYER_ID"],
#                                         slug=f'{player["PLAYER_FULL_NAME"]} + {player["PLAYER_ID"]}',
#                                         name=player["PLAYER_FULL_NAME"],
#                                         photo=f'https://www.flashscore.com/res/image/data/{player["LPI"]}',
#                                         position_name=player["PLAYER_POSITION"],
#                                         description=player,
#                                         main_player=False,
#                                         number=player["PLAYER_NUMBER"],
#                                     )
#                                 event.home_team.players.add(player)
#                             elif team_line == 2 :
#                                 if formation_name == 'Starting Lineups':
#                                     player = Player.objects.create(
#                                         player_id=player["PLAYER_ID"],
#                                         slug=f'{player["PLAYER_FULL_NAME"]} + {player["PLAYER_ID"]}',
#                                         name=player["PLAYER_FULL_NAME"],
#                                         photo=f'https://www.flashscore.com/res/image/data/{player["LPI"]}',
#                                         position_name=player["PLAYER_POSITION"],
#                                         description=player,
#                                         main_player=True,
#                                         number=player["PLAYER_NUMBER"],
#                                     )
#                                 else:
#                                     player = Player.objects.create(
#                                         player_id=player["PLAYER_ID"],
#                                         slug=f'{player["PLAYER_FULL_NAME"]} + {player["PLAYER_ID"]}',
#                                         name=player["PLAYER_FULL_NAME"],
#                                         photo=f'https://www.flashscore.com/res/image/data/{player["LPI"]}',
#                                         position_name=player["PLAYER_POSITION"],
#                                         description=player,
#                                         main_player=False,
#                                         number=player["PLAYER_NUMBER"],
#                                     )
#                                 event.away_team.players.add(player)
#     return {"response": "get_team_players_second successfully"}
#     #
#     # return HttpResponse("Data "
#     #                     "fetched successfully")
#
# @shared_task
# def get_h2h_second():
#
#     events = Events.objects.filter(second_event_api_id__isnull = False)
#     for event in events:
#         second_url = "https://flashlive-sports.p.rapidapi.com/v1/events/h2h"
#         second_querystring = {"locale": "en_INT", "event_id": event.second_event_api_id}
#         # H2H события
#         second_response = requests.get(second_url, headers=HEADER_FOR_SECOND_API, params=second_querystring)
#         if second_response.status_code == 200:
#             second_response_data = second_response.json().get("DATA", [])
#             for el in second_response_data:
#                 groups = el.get("GROUPS")
#                 for group in groups:
#                     print('----group-----', group)
#                     items = group.get("ITEMS", [])
#
#                     for item in items:
#                         hi = item.get("HOME_IMAGES")
#                         ai = item.get("AWAY_IMAGES")
#                         if hi is not None and ai is not None:
#                             if not H2H.objects.filter(
#                                     home_score=item.get("HOME_SCORE_FULL"),
#                                     away_score=item.get("AWAY_SCORE_FULL"),
#                                     name=item.get("EVENT_NAME"),
#                                     home_team_NAME=item.get("HOME_PARTICIPANT"),
#                                     home_team_LOGO=item.get("HOME_IMAGES")[-1],
#                                     away_team_NAME=item.get("AWAY_PARTICIPANT"),
#                                     away_team_LOGO=item.get("AWAY_IMAGES")[-1],
#                                     league=item.get("EVENT_NAME"),
#                                     start_at=datetime.utcfromtimestamp(item.get('START_TIME')),
#                                     h_result=item.get("H_RESULT"),
#                                     team_mark=item.get("TEAM_MARK"),
#                             ).exists():
#                                 h2h = H2H.objects.create(
#                                     home_score=item.get("HOME_SCORE_FULL"),
#                                     away_score=item.get("AWAY_SCORE_FULL"),
#                                     name=item.get("EVENT_NAME"),
#                                     home_team_NAME=item.get("HOME_PARTICIPANT"),
#                                     home_team_LOGO=item.get("HOME_IMAGES")[-1],
#                                     away_team_NAME=item.get("AWAY_PARTICIPANT"),
#                                     away_team_LOGO=item.get("AWAY_IMAGES")[-1],
#                                     league=item.get("EVENT_NAME"),
#                                     start_at=datetime.utcfromtimestamp(item.get('START_TIME')),
#                                     h_result=item.get("H_RESULT"),
#                                     team_mark=item.get("TEAM_MARK"),
#                                 )
#                                 event.h2h.add(h2h)
#                                 event.save()
#     # return HttpResponse("Data fetched successfully")
#     return {"response": "get_h2h_second successfully"}

