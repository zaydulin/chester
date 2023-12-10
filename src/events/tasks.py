from celery import shared_task
from django.http import HttpResponse
import requests

from datetime import datetime
from .models import Rubrics, Season, Team, Events, H2H


@shared_task
def add_sport_events_list_second():
    second_url = "https://flashlive-sports.p.rapidapi.com/v1/events/list"

    base_querystring = {"timezone": "-4", "indent_days": "-1", "locale": "ru_RU", "sport_id": ""}
    second_api_rubric_ids = Rubrics.objects.filter(second_api=True).values_list("api_id", flat=True).distinct()

    for rubric_id in second_api_rubric_ids:
        rubric_id_q = str(rubric_id)
        querystring = {"timezone": "-4", "indent_days": "7", "locale": "ru_RU", "sport_id": rubric_id_q}
        second_headers = {
            "X-RapidAPI-Key": "b4e32c39demsh21dc3591499b4f3p144d40jsn9a29de0bcb2a",
            "X-RapidAPI-Host": "flashlive-sports.p.rapidapi.com",
        }
        rubrics = Rubrics.objects.get(second_api=True, api_id=rubric_id)
        second_response = requests.get(second_url, headers=second_headers, params=querystring)
        if second_response.status_code == 200:
            response_data = second_response.json()
            for event_data in response_data.get("DATA", []):
                # Создайте записи для команд (Team)
                events = event_data.get("EVENTS")
                try:
                    season = Season.objects.get(
                        rubrics=rubrics, season_second_api_id=event_data.get("TOURNAMENT_SEASON_ID")
                    )
                except:
                    season = Season.objects.create(
                        rubrics=rubrics,
                        season_second_api_id=event_data.get("TOURNAMENT_SEASON_ID"),
                        season_name=event_data.get("NAME"),
                        logo_league=event_data.get("TOURNAMENT_IMAGE"),
                        country=event_data.get("COUNTRY_NAME"),
                    )
                for event in events:
                    homeimg_base = event.get("HOME_IMAGES")
                    awayimg_base = event.get("AWAY_IMAGES")
                    if homeimg_base is not None and awayimg_base is not None:
                        try:
                            home_team = Team.objects.get(second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1])
                        except:

                            home_team = Team.objects.create(
                                second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1],
                                name=event.get("HOME_NAME"),
                                logo=event.get("HOME_IMAGES")[-1],
                                rubrics=rubrics,
                            )
                        try:
                            away_team = Team.objects.get(second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1])
                        except:
                            away_team = Team.objects.create(
                                second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1],
                                name=event.get("AWAY_NAME"),
                                logo=event.get("AWAY_IMAGES")[-1],
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
                                status=2,
                                home_team=home_team,
                                away_team=away_team,
                                home_score=event.get("HOME_SCORE_CURRENT"),
                                away_score=event.get("AWAY_SCORE_CURRENT"),
                                half=event.get("ROUND"),
                                section=season,
                            )
        else:
            return HttpResponse(f"Error  - {second_response.status_code} - {second_response.json()}")
    add_sport_events_list_second_online_gou()
    return HttpResponse("Data fetched successfully")


def add_sport_events_list_second_online_gou():
    second_url = "https://flashlive-sports.p.rapidapi.com/v1/events/live-list"

    second_api_rubric_ids = Rubrics.objects.filter(second_api=True).values_list("api_id", flat=True).distinct()

    for rubric_id in second_api_rubric_ids:
        rubric_id_q = str(rubric_id)
        querystring = {"timezone": "-4", "locale": "ru_RU", "sport_id": rubric_id_q}

        second_headers = {
            "X-RapidAPI-Key": "b4e32c39demsh21dc3591499b4f3p144d40jsn9a29de0bcb2a",
            "X-RapidAPI-Host": "flashlive-sports.p.rapidapi.com",
        }
        rubrics = Rubrics.objects.get(second_api=True, api_id=rubric_id)
        second_response = requests.get(second_url, headers=second_headers, params=querystring)
        if second_response.status_code == 200:
            response_data = second_response.json()
            for event_data in response_data.get("DATA", []):
                # Создайте записи для команд (Team)
                events = event_data.get("EVENTS")
                try:
                    season = Season.objects.get(
                        rubrics=rubrics, season_second_api_id=event_data.get("TOURNAMENT_SEASON_ID")
                    )
                except Season.DoesNotExist:
                    season = Season.objects.create(
                        rubrics=rubrics,
                        season_second_api_id=event_data.get("TOURNAMENT_SEASON_ID"),
                        season_name=event_data.get("NAME"),
                        logo_league=event_data.get("TOURNAMENT_IMAGE"),
                        country=event_data.get("COUNTRY_NAME"),
                    )
                for event in events:
                    homeimg_base = event.get("HOME_IMAGES")
                    awayimg_base = event.get("AWAY_IMAGES")
                    if homeimg_base is not None and awayimg_base is not None:
                        try:
                            home_team = Team.objects.get(second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1])
                        except Team.DoesNotExist():
                            home_team = Team.objects.create(
                                second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1],
                                name=event.get("HOME_NAME"),
                                logo=event.get("HOME_IMAGES")[-1],
                                rubrics=rubrics,
                            )
                        try:
                            away_team = Team.objects.get(second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1])
                        except Team.DoesNotExist:
                            away_team = Team.objects.create(
                                second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1],
                                name=event.get("AWAY_NAME"),
                                logo=event.get("AWAY_IMAGES")[-1],
                                rubrics=rubrics,
                            )

                        if not Events.objects.filter(
                            rubrics=rubrics,
                            second_event_api_id=event.get("EVENT_ID"),
                        ).exists():
                            Events.objects.create(
                                rubrics=rubrics,
                                second_event_api_id=event.get("EVENT_ID"),
                                start_at=datetime.utcfromtimestamp(event.get("START_TIME")),
                                name=event_data.get("NAME_PART_2"),
                                description=event_data,
                                title=event_data.get("SHORT_NAME"),
                                status=1,
                                home_team=home_team,
                                away_team=away_team,
                                home_score=event.get("HOME_SCORE_CURRENT"),
                                away_score=event.get("AWAY_SCORE_CURRENT"),
                                half=event.get("ROUND"),
                                section=season,
                            )
        else:
            return HttpResponse(f"Error  - {second_response.status_code} - {second_response.json()}")

    return HttpResponse("Data fetched successfully")


@shared_task
def fetch_event_data_for_second():
    events = Events.objects.filter(second_event_api_id__isnull=False)
    url = "https://flashlive-sports.p.rapidapi.com/v1/events/data"

    headers = {
        "X-RapidAPI-Key": "b4e32c39demsh21dc3591499b4f3p144d40jsn9a29de0bcb2a",
        "X-RapidAPI-Host": "flashlive-sports.p.rapidapi.com",
    }
    for event in events:
        querystring = {"locale": "en_INT", "event_id": event.second_event_api_id}
        response = requests.get(url, headers=headers, params=querystring)
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
        second_url = "https://flashlive-sports.p.rapidapi.com/v1/events/h2h"

        second_querystring = {"locale": "en_INT", "event_id": event.second_event_api_id}

        second_response = requests.get(second_url, headers=headers, params=second_querystring)
        if second_response.status_code == 200:
            second_response_data = second_response.json().get("DATA", [])
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
                                H2H.objects.create(
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

    return HttpResponse("Data fetched successfully")
