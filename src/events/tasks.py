from celery import shared_task
import requests
from datetime import datetime
from .models import Rubrics, Season, Team, Events, H2H, Country
from django.db.models import Q
from events.models import Rubrics, Events, Team, Season, Player, Incidents, Periods, GameStatistic, H2H, TennisPoints, \
  TennisGames, Points , Country,Stages , IncidentParticipants



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


HEADER_FOR_LIVE_STREAM = {
    "X-RapidAPI-Key": "11047ab519mshed06c5cc71509fep168f75jsn077ef01d5d10",
	"X-RapidAPI-Host": "free-football-soccer-videos1.p.rapidapi.com"
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
                # second_api=True,
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


@shared_task
def create_events_of_tournament_id1():
    create_events_of_tournament(1)
    return {"response": "create_events_of_tournament successfully"}


@shared_task
def create_events_of_tournament_id2():
    create_events_of_tournament(2)
    return {"response": "create_events_of_tournament successfully"}


@shared_task
def create_events_of_tournament_id3():
    create_events_of_tournament(3)
    return {"response": "create_events_of_tournament successfully"}


@shared_task
def create_events_of_tournament_id4():
    create_events_of_tournament(4)
    return {"response": "create_events_of_tournament successfully"}


@shared_task
def create_events_of_tournament_id6():
    create_events_of_tournament(6)
    return {"response": "create_events_of_tournament successfully"}


@shared_task
def create_events_of_tournament_id7():
    create_events_of_tournament(7)
    return {"response": "create_events_of_tournament successfully"}


@shared_task
def create_events_of_tournament_id12():
    create_events_of_tournament(12)
    return {"response": "create_events_of_tournament successfully"}


@shared_task
def create_events_of_tournament_id13():
    create_events_of_tournament(13)
    return {"response": "create_events_of_tournament successfully"}


@shared_task
def create_events_of_tournament_id15():
    create_events_of_tournament(15)
    return {"response": "create_events_of_tournament successfully"}


@shared_task
def create_events_of_tournament_id21():
    create_events_of_tournament(21)
    return {"response": "create_events_of_tournament successfully"}

@shared_task
def create_events_of_tournament_id25():
    create_events_of_tournament(25)
    return {"response": "create_events_of_tournament successfully"}

@shared_task
def create_events_of_tournament_id36():
    create_events_of_tournament(36)
    return {"response": "create_events_of_tournament successfully"}


@shared_task
def fetch_event_data(rubric_id):
    url = "https://flashlive-sports.p.rapidapi.com/v1/events/live-update"
    incidents_url = "https://flashlive-sports.p.rapidapi.com/v1/events/summary-incidents"
    statistics_url = "https://flashlive-sports.p.rapidapi.com/v1/events/statistics"

    querystring = {"locale": "ru_RU", "sport_id": rubric_id}

    rubric = Rubrics.objects.get(api_id = rubric_id)
    incidents_events = Events.objects.filter(status=1, rubrics=rubric)
    gamestatistic_events = Events.objects.filter(status=1, rubrics=rubric)
    response = requests.get(url, headers=HEADER_FOR_SECOND_API, params=querystring)
    if response.status_code == 200:
        response_data = response.json().get("DATA", [])
        for item in response_data:
            event_id = item.get("EVENT_ID")
            status = item.get("STAGE_TYPE")
            hsc = item.get("HOME_SCORE_CURRENT")
            asc = item.get("AWAY_SCORE_CURRENT")
            event = Events.objects.filter(second_event_api_id=event_id, rubrics=rubric).first()
            if event:
                event.home_score = hsc
                event.away_score = asc
                event.save()

                if status == "FINISHED":
                    event.status = 2
                    event.save()
                elif status == "LIVE":
                    event.status = 1
                    event.save()

    else:
        return {"response": f"Error fetch - {response.status_code} - {response.json()}"}

    #incidents
    for event in incidents_events:
        incidents_querystring = {"locale": "ru_RU", "event_id": event.second_event_api_id}
        incidents_response = requests.get(incidents_url, headers=HEADER_FOR_SECOND_API, params=incidents_querystring)
        if incidents_response.status_code == 200:
            incidents_response_data = incidents_response.json().get("DATA", [])
            for data in incidents_response_data:
                stage_name = data.get('STAGE_NAME',0)
                if event.periods.filter(period_number=stage_name,event_api_id = event.second_event_api_id).exists():
                    period = event.periods.get(period_number=stage_name)
                    result_home  = data.get('RESULT_HOME')
                    result_away = data.get('RESULT_AWAY')
                    if result_home :
                        period.home_score = result_home
                    if result_away :
                        period.away_score = result_away
                    period.save()
                else:
                    period = Periods.objects.create(event_api_id = event.second_event_api_id,home_score = data.get('RESULT_HOME',0),away_score = data.get('RESULT_AWAY',0) ,period_number= stage_name )
                    event.periods.add(period)
                    event.save()
                data_items = data.get("ITEMS", [])
                for item in data_items:
                    incident_id = item.get('INCIDENT_ID')
                    incident_team = item.get('INCIDENT_TEAM')
                    incident_time = item.get('INCIDENT_TIME','0')
                    if event.incidents.filter(incident_api_id = incident_id, rubrics = rubric).exists():
                        incident = event.incidents.get(incident_api_id = incident_id,rubrics = rubric)
                    else:
                        incident = Incidents.objects.create(
                            rubrics = rubric,
                            incident_api_id = incident_id,
                            incident_team = incident_team,
                            time = incident_time
                        )
                    incident_participants = item.get('INCIDENT_PARTICIPANTS',[])
                    for participant in incident_participants:
                        incident_type = participant.get("INCIDENT_TYPE")
                        participant_name = participant.get("PARTICIPANT_NAME")
                        participant_id = participant.get("PARTICIPANT_ID")
                        incident_name = participant.get("PARTICIPANT_NAME")
                        incident_participant = IncidentParticipants.objects.create(
                            incident_type= incident_type,
                            participant_name = participant_name,
                            incident_name = incident_name,
                            participant_id = participant_id
                        )
                        incident.incident_participants.add(incident_participant)
                        incident.save()
                    event.incidents.add(incident)
                    event.save()
    # gamestatistic
    for event in gamestatistic_events:
        gamestatistic_querystring = {"locale": "ru_RU", "event_id":event.second_event_api_id}
        gamestatistic_response = requests.get(statistics_url, headers=HEADER_FOR_SECOND_API, params=gamestatistic_querystring)
        if gamestatistic_response.status_code == 200:
            gamestatistic_response_data = gamestatistic_response.json().get("DATA", [])
            for data in gamestatistic_response_data:
                stage_name = data.get("STAGE_NAME",0)
                groups = data.get("GROUPS")
                for group in groups:
                    items = group.get("ITEMS", [])
                    for item in items:
                        incident_name = item.get("INCIDENT_NAME")
                        value_home = item.get("VALUE_HOME")
                        value_away = item.get("VALUE_AWAY")
                        if event.statistic.filter(period=stage_name,name=incident_name,home=value_home,away=value_away ).exists():
                            pass
                        else:
                            gamestatistic = GameStatistic.objects.create(
                                period=stage_name,
                                name=incident_name,
                                home=value_home,
                                away=value_away
                            )
                            event.statistic.add(gamestatistic)
                            event.save()

    return {"response": "fetch_event_data_for_second successfully"}

#обновление событий
@shared_task
def fetch_event_data_id1():
    fetch_event_data(1)
    return {"response": "fetch_event_data_id1 successfully"}


@shared_task
def fetch_event_data_id2():
    fetch_event_data(2)
    return {"response": "fetch_event_data_id2 successfully"}


@shared_task
def fetch_event_data_id3():
    fetch_event_data(3)
    return {"response": "fetch_event_data_id3 successfully"}


@shared_task
def fetch_event_data_id4():
    fetch_event_data(4)
    return {"response": "fetch_event_data_id4 successfully"}


@shared_task
def fetch_event_data_id6():
    fetch_event_data(6)
    return {"response": "fetch_event_data_id6 successfully"}


@shared_task
def fetch_event_data_id7():
    fetch_event_data(7)
    return {"response": "fetch_event_data_id7 successfully"}


@shared_task
def fetch_event_data_id12():
    fetch_event_data(12)
    return {"response": "fetch_event_data_id12 successfully"}


@shared_task
def fetch_event_data_id13():
    fetch_event_data(13)
    return {"response": "fetch_event_data_id13 successfully"}


@shared_task
def fetch_event_data_id15():
    fetch_event_data(15)
    return {"response": "fetch_event_data_id15 successfully"}


@shared_task
def fetch_event_data_id21():
    fetch_event_data(21)
    return {"response": "fetch_event_data_id21 successfully"}

@shared_task
def fetch_event_data_id25():
    fetch_event_data(25)
    return {"response": "fetch_event_data_id25 successfully"}

@shared_task
def fetch_event_data_id36():
    fetch_event_data(36)
    return {"response": "fetch_event_data_id36 successfully"}

@shared_task
def get_match_stream_link():
    url = "https://free-football-soccer-videos1.p.rapidapi.com/v1/"
    response = requests.get(url, headers=HEADER_FOR_LIVE_STREAM)
    rubric_id = 1
    if response.status_code == 200:
        data = response.json()
        for item in data:
            side1 = item.get("side1").get("name")
            side2 = item.get("side2").get("name")
            date = item.get("date")
            date_only = date.split("T")[0]
            embed = item.get("embed")
            name = item.get("competition").get("name")
            event = Events.objects.filter(rubrics__api_id=rubric_id,home_team__name = side1,away_team__name = side2,start_at__startswith=date_only).first()
            try:
                event.match_stream_link = embed
                event.save()
            except:
                pass
    return {"response": "get_match_stream_link successfully"}

@shared_task
def create_additional_info_for_events(rubric_id):
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    rubric = Rubrics.objects.get(api_id=rubric_id)
    events_h2h = Events.objects.filter(~Q(status=2), h2h_status=False, rubrics=rubric,second_event_api_id__isnull=False, start_at__startswith=today_str)
    for event in events_h2h:
        url = "https://flashlive-sports.p.rapidapi.com/v1/events/h2h"
        querystring = {"locale": "en_INT", "event_id": event.second_event_api_id}
        response = requests.get(url, headers=HEADER_FOR_SECOND_API, params=querystring)
        if response.status_code == 200:
            second_response_data = response.json().get("DATA", [])
            for el in second_response_data:
                groups = el.get("GROUPS")
                for group in groups:
                    items = group.get("ITEMS", [])
                    for item in items:
                        hi = item.get("HOME_IMAGES")
                        ai = item.get("AWAY_IMAGES")
                        if hi is not None and ai is not None:
                            if not H2H.objects.filter(
                                home_score=item.get("HOME_SCORE_FULL"),
                                away_score=item.get("AWAY_SCORE_FULL"),
                                name=item.get("EVENT_NAME"),
                                home_team_NAME=item.get("HOME_PARTICIPANT"),
                                home_team_LOGO=item.get("HOME_IMAGES")[-1],
                                away_team_NAME=item.get("AWAY_PARTICIPANT"),
                                away_team_LOGO=item.get("AWAY_IMAGES")[-1],
                                league=item.get("EVENT_NAME"),
                                start_at=datetime.utcfromtimestamp(item.get("START_TIME")),
                                h_result=item.get("H_RESULT"),
                                team_mark=item.get("TEAM_MARK"),
                            ).exists():
                                h2h = H2H.objects.create(
                                    home_score=item.get("HOME_SCORE_FULL"),
                                    away_score=item.get("AWAY_SCORE_FULL"),
                                    name=item.get("EVENT_NAME"),
                                    home_team_NAME=item.get("HOME_PARTICIPANT"),
                                    home_team_LOGO=item.get("HOME_IMAGES")[-1],
                                    away_team_NAME=item.get("AWAY_PARTICIPANT"),
                                    away_team_LOGO=item.get("AWAY_IMAGES")[-1],
                                    league=item.get("EVENT_NAME"),
                                    start_at=datetime.utcfromtimestamp(item.get("START_TIME")),
                                    h_result=item.get("H_RESULT"),
                                    team_mark=item.get("TEAM_MARK"),
                                )
                                event.h2h.add(h2h)
                                event.save()
                            else:
                                h2h = H2H.objects.filter(
                                home_score=item.get("HOME_SCORE_FULL"),
                                away_score=item.get("AWAY_SCORE_FULL"),
                                name=item.get("EVENT_NAME"),
                                home_team_NAME=item.get("HOME_PARTICIPANT"),
                                home_team_LOGO=item.get("HOME_IMAGES")[-1],
                                away_team_NAME=item.get("AWAY_PARTICIPANT"),
                                away_team_LOGO=item.get("AWAY_IMAGES")[-1],
                                league=item.get("EVENT_NAME"),
                                start_at=datetime.utcfromtimestamp(item.get("START_TIME")),
                                h_result=item.get("H_RESULT"),
                                team_mark=item.get("TEAM_MARK"),
                                ).first()
                                event.h2h.add(h2h)
                                event.save()
            event.h2h_status = True
            event.save()
        else:
            return {"response": f"Error create_additional_info_for_events - {response.status_code} - {response.json()}"}
    second_url = "https://flashlive-sports.p.rapidapi.com/v1/events/lineups"
    events = Events.objects.filter(rubrics__api_id=rubric_id)
    for event in events:
        querystring = {"locale": "ru_RU", "event_id": event.second_event_api_id}
        response = requests.get(second_url, headers=HEADER_FOR_SECOND_API, params=querystring)
        if response.status_code == 200:
            response_data = response.json().get("DATA")
            for data in response_data:
                formation_name = data.get("FORMATION_NAME")
                formations = data.get("FORMATIONS", [])
                for formation in formations:
                    team_line = formation.get("FORMATION_LINE")
                    members = formation.get("MEMBERS", [])
                    for player in members:
                        try:
                            player = Player.objects.get(player_id=player["id"])
                        except Player.DoesNotExist:
                            if team_line == 1:
                                if formation_name == 'Starting Lineups':
                                    player = Player.objects.create(
                                        player_id=player["PLAYER_ID"],
                                        slug=f'{player["PLAYER_FULL_NAME"]} + {player["PLAYER_ID"]}',
                                        name=player["PLAYER_FULL_NAME"],
                                        photo=f'https://www.flashscore.com/res/image/data/{player["LPI"]}',
                                        position_name=player["PLAYER_POSITION"],
                                        description=player,
                                        main_player=True,
                                        number=player["PLAYER_NUMBER"],
                                    )
                                else:
                                    player = Player.objects.create(
                                        player_id=player["PLAYER_ID"],
                                        slug=f'{player["PLAYER_FULL_NAME"]} + {player["PLAYER_ID"]}',
                                        name=player["PLAYER_FULL_NAME"],
                                        photo=f'https://www.flashscore.com/res/image/data/{player["LPI"]}',
                                        position_name=player["PLAYER_POSITION"],
                                        description=player,
                                        main_player=False,
                                        number=player["PLAYER_NUMBER"],
                                    )
                                event.home_team.players.add(player)
                            elif team_line == 2:
                                if formation_name == 'Starting Lineups':
                                    player = Player.objects.create(
                                        player_id=player["PLAYER_ID"],
                                        slug=f'{player["PLAYER_FULL_NAME"]} + {player["PLAYER_ID"]}',
                                        name=player["PLAYER_FULL_NAME"],
                                        photo=f'https://www.flashscore.com/res/image/data/{player["LPI"]}',
                                        position_name=player["PLAYER_POSITION"],
                                        description=player,
                                        main_player=True,
                                        number=player["PLAYER_NUMBER"],
                                    )
                                else:
                                    player = Player.objects.create(
                                        player_id=player["PLAYER_ID"],
                                        slug=f'{player["PLAYER_FULL_NAME"]} + {player["PLAYER_ID"]}',
                                        name=player["PLAYER_FULL_NAME"],
                                        photo=f'https://www.flashscore.com/res/image/data/{player["LPI"]}',
                                        position_name=player["PLAYER_POSITION"],
                                        description=player,
                                        main_player=False,
                                        number=player["PLAYER_NUMBER"],
                                    )
                                event.away_team.players.add(player)
    return {"response": "create_additional_info_for_events successfully"}


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
