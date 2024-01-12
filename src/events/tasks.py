from celery import shared_task
import requests
from datetime import datetime
from .models import Rubrics, Season, Team, Events, H2H, Country
from django.db.models import Q
from events.models import Rubrics, Events, Team, Season, Player, Incidents, Periods, GameStatistic, H2H, TennisPoints, \
    TennisGames, Points, Country, Stages

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

EVENT_STATUSES = {
    'LIVE': 1,
    'FINISHED': 2,
    'SCHEDULED': 3
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


# # done optimization
# @shared_task
# def create_tournament():
#     tournaments_list_url = "https://flashlive-sports.p.rapidapi.com/v1/tournaments/list"
#
#     for rubric_id in [1]:
#         rubric_id_q = str(rubric_id)
#         querystring_tournaments_list = {"sport_id": rubric_id_q, "locale": "ru_RU"}
#         rubrics = Rubrics.objects.get(api_id=rubric_id)
#         response_tournaments_list = requests.get(
#             tournaments_list_url,
#             headers=HEADER_FOR_SECOND_API,
#             params=querystring_tournaments_list
#         )
#         if response_tournaments_list.status_code == 200:
#             tournaments_data = response_tournaments_list.json()
#             for tournament_data in tournaments_data.get("DATA", []):
#                 country_name = tournament_data.get('COUNTRY_NAME')
#                 country, created = Country.objects.get_or_create(
#                     name=country_name
#                 )
#                 season_id = tournament_data.get("ACTUAL_TOURNAMENT_SEASON_ID")
#                 fields = {
#                     "league_name": tournament_data.get("LEAGUE_NAME"),
#                     "country": country
#                 }
#                 season, created = Season.objects.get_or_create(
#                     rubrics=rubrics,
#                     season_id=season_id,
#                     defaults=fields
#                 )
#                 stages = tournament_data.get("STAGES")
#                 stages_list = []
#                 for stage in stages:
#                     stage_id = stage.get("STAGE_ID")
#                     stage_name = stage.get("STAGE_NAME")
#                     stage_db = Stages(
#                         stage_id=stage_id
#                     )
#                     if stage_name:
#                         stage_db.stage_name = stage_name
#                     stages_list.append(stage_db)
#                 stages = Stages.objects.bulk_create(stages_list)
#                 season.stages.add(*stages)
#         else:
#             return {
#                 "response": f"Error  - {response_tournaments_list.status_code} - {response_tournaments_list.json()}"}
#
#     return {"response": "create_tournament successfully"}
#

def create_events_of_tournament(rubric_id):
    second_url = "https://flashlive-sports.p.rapidapi.com/v1/tournaments/fixtures"
    seasons = Season.objects.filter(rubrics__api_id=rubric_id)
    for season in seasons:
        stages = season.stages.all()
        for stage in stages:
            querystring = {"locale": "ru_RU", "tournament_stage_id": str(stage.stage_id), "page": "1"}
            rubrics = Rubrics.objects.get(
                second_api=True,
                api_id=rubric_id
            )
            second_response = requests.get(
                second_url,
                headers=HEADER_FOR_SECOND_API,
                params=querystring
            )
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
                    country_name = event_data.get("COUNTRY_NAME")
                    if not country_name:
                        country_from_db = Country.objects.get_or_create(
                            name="Мир"
                        )
                    else:
                        country_from_db, created = Country.objects.get_or_create(
                            name=event_data.get("COUNTRY_NAME")
                        )
                    season, created = Season.objects.get_or_create(
                        rubrics=rubrics,
                        season_id=event_data.get("TOURNAMENT_SEASON_ID")
                    )
                    season.logo_league = correct_logo_season
                    season.season_name = event_data.get("NAME")
                    season.season_second_api_id = event_data.get("TOURNAMENT_STAGE_ID")
                    if created:
                        season.country = country_from_db
                        season.season_second_api_id = event_data.get("TOURNAMENT_STAGE_ID")
                    season.save()
                    events_list = []
                    for event in events:
                        homeimg_base = event.get("HOME_IMAGES")
                        awayimg_base = event.get("AWAY_IMAGES")
                        status_id = EVENT_STATUSES[event.get("STAGE_TYPE")]
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
                            fields = {
                                "name": event.get("HOME_NAME"),
                                "logo": correct_home_logo,
                                "rubrics": rubrics
                            }
                            home_team, created = Team.objects.get_or_create(
                                second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1],
                                defaults=fields
                            )
                            fields = {
                                "name": event.get("AWAY_NAME"),
                                "logo": correct_away_logo,
                                "rubrics": rubrics
                            }
                            away_team, created = Team.objects.get_or_create(
                                second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1],
                                defaults=fields
                            )
                            if not Events.objects.filter(
                                    rubrics=rubrics, second_event_api_id=event.get("EVENT_ID")
                            ).exists():
                                events_list.append(Events(
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
                                ))
                    Events.objects.bulk_create(events_list)
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

#
# @shared_task
# def create_events_of_tournament_id1():
#     create_events_of_tournament(1)
#     return {"response": "create_events_of_tournament successfully"}
#
#
# @shared_task
# def create_events_of_tournament_id2():
#     create_events_of_tournament(2)
#     return {"response": "create_events_of_tournament successfully"}
#
#
# @shared_task
# def create_events_of_tournament_id3():
#     create_events_of_tournament(3)
#     return {"response": "create_events_of_tournament successfully"}
#
#
# @shared_task
# def create_events_of_tournament_id4():
#     create_events_of_tournament(4)
#     return {"response": "create_events_of_tournament successfully"}
#
#
# @shared_task
# def create_events_of_tournament_id6():
#     create_events_of_tournament(6)
#     return {"response": "create_events_of_tournament successfully"}
#
#
# @shared_task
# def create_events_of_tournament_id11():
#     create_events_of_tournament(11)
#     return {"response": "create_events_of_tournament successfully"}
#
#
# @shared_task
# def create_events_of_tournament_id12():
#     create_events_of_tournament(12)
#     return {"response": "create_events_of_tournament successfully"}
#
#
# @shared_task
# def create_events_of_tournament_id15():
#     create_events_of_tournament(15)
#     return {"response": "create_events_of_tournament successfully"}


@shared_task
def create_events_of_tournament_id21():
    create_events_of_tournament(21)
    return {"response": "create_events_of_tournament successfully"}

#
# @shared_task
# def create_events_of_tournament_id25():
#     create_events_of_tournament(25)
#     return {"response": "create_events_of_tournament successfully"}
#
#
# @shared_task
# def create_events_of_tournament_id36():
#     create_events_of_tournament(36)
#     return {"response": "create_events_of_tournament successfully"}


@shared_task
def fetch_event_data_for_second():
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    events = Events.objects.filter(
        ~Q(status=2),
        second_event_api_id__isnull=False,
        start_at__startswith=today_str
    )
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
            event.status = EVENT_STATUSES[status]
            event.save()
        else:
            return {"response": f"Error fetch - {response.status_code} - {response.json()}"}
        # пока оставить
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

#
# # не нужное,но пока не удалять
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
#                     correct_logo_season = logo_season.replace('www.', 'static.')
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
#                                 rubrics=rubrics, second_event_api_id=event.get("EVENT_ID")
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
#             #         return HttpResponse(f"Error  - {second_response.status_code} - {second_response.json()}")
#             # return HttpResponse("Data fetched successfully")
#             return {"response": f"Error  - {second_response.status_code} - {second_response.json()}"}
#         return {"response": "add_sport_events_list_second successfully"}
#
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
#                     correct_logo_season = logo_season.replace('www.', 'static.')
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
#                                 rubrics=rubrics, second_event_api_id=event.get("EVENT_ID")
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
#             #         return HttpResponse(f"Error  - {second_response.status_code} - {second_response.json()}")
#             # return HttpResponse("Data fetched successfully")
#             return {"response": f"Error  - {second_response.status_code} - {second_response.json()}"}
#         return {"response": "add_sport_events_list_second_future successfully"}
#
#
# @shared_task
# def add_sport_events_list_second_online_gou():
#     second_url = "https://flashlive-sports.p.rapidapi.com/v1/events/live-list"
#
#     second_api_rubric_ids = Rubrics.objects.filter(second_api=True).values_list("api_id", flat=True).distinct()
#
#     for rubric_id in second_api_rubric_ids:
#         rubric_id_q = str(rubric_id)
#         querystring = {"timezone": "-4", "sport_id": rubric_id_q, "locale": "ru_RU"}
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
#
#
# @shared_task
# def get_team_players_second():
#     url = "https://flashlive-sports.p.rapidapi.com/v1/events/lineups"
#     events = Events.objects.filter(second_event_api_id__isnull=False, status=1)
#     for event in events:
#         querystring = {"locale": "ru_RU", "event_id": event.second_event_api_id}
#         response = requests.get(url, headers=HEADER_FOR_SECOND_API, params=querystring)
#         if response.status_code == 200:
#             response_data = response.json().get("DATA")
#             for data in response_data:
#                 formation_name = data.get("FORMATION_NAME")
#                 formations = data.get("FORMATIONS", [])
#                 for formation in formations:
#                     team_line = formation.get("FORMATION_LINE")
#                     members = formation.get("MEMBERS", [])
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
#                                 event.home_team.players.add(player)
#                             elif team_line == 2:
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
#
# @shared_task
# def get_h2h_second():
#     events = Events.objects.filter(second_event_api_id__isnull=False)
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
