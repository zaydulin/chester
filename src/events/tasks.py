import json
from time import sleep
from django.utils import timezone
from django.db.utils import DataError
from celery import shared_task
from django.http import HttpResponse
import requests
from datetime import date ,timedelta ,datetime
from .models import Rubrics, Season, Team, Events, H2H, Country
from django.db.models import Q
import time
from googletrans import Translator
from events.models import Rubrics, Events, Team, Season, Player, Incidents, Periods, GameStatistic, H2H, TennisPoints, \
    TennisGames, Points , Country
import re


HEADER_FOR_FIRST_API = {
        "X-RapidAPI-Key": "3b1726a15fmshc58a145e91a5846p197521jsn5a6af790e789",
        "X-RapidAPI-Host": "sportscore1.p.rapidapi.com"
    }

HEADER_FOR_SECOND_API = {
  "X-RapidAPI-Key": "3b1726a15fmshc58a145e91a5846p197521jsn5a6af790e789",
  "X-RapidAPI-Host": "flashlive-sports.p.rapidapi.com"
}

def translate_to_russian(name):
    # Слишком много запросов к апи - не работает такска add_sport_events_list
    #
    # # Создайте экземпляр переводчика
    # translator = Translator()
    #
    # # Переведите имя на русский язык
    # translated_name = translator.translate(name, src="en", dest="ru").text

    # return translated_name
    return name

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

@shared_task
def add_sport_events_list():
    base_url = "https://sportscore1.p.rapidapi.com/sports/{}/events/date/{}"

    current_date = date.today()
    # это логи ?
    # with open('/var/www/chester/add_sport_events_list.txt', 'w') as file:
    #     file.write('its works\n')
    end_date = current_date +timedelta(days=6)
    api_rubric_ids = Rubrics.objects.filter(second_api=False).values_list('api_id', flat=True).distinct()
    count_event = 0
    for api_rubric_id in api_rubric_ids :
         current_date = date.today()
         while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            url = base_url.format(api_rubric_id, date_str)
            querystring = {"page": "1"}
            response = requests.get(url, headers=HEADER_FOR_FIRST_API, params=querystring)
            if response.status_code == 200:
                data = response.json().get("data", [])
                for event_data in data:
                    home_team_data = event_data.get("home_team", {})
                    away_team_data = event_data.get("away_team", {})

                    rubric = Rubrics.objects.get(second_api = False,api_id=api_rubric_id)
                    try:
                        home_team = Team.objects.get(api_team_id=home_team_data.get("id"))
                    except  Team.DoesNotExist  :

                        home_team = Team.objects.create(
                            name=home_team_data.get("name"),
                            rubrics=rubric,
                            api_team_id=home_team_data.get("id"),
                            logo=home_team_data.get("logo"),
                            description = home_team_data
                        )

                    try :
                        away_team = Team.objects.get(api_team_id=away_team_data.get("id"))
                    except  Team.DoesNotExist:

                        away_team = Team.objects.create(
                            name=away_team_data.get("name"),
                            rubrics=rubric,
                            api_team_id=away_team_data.get("id") ,

                            logo =away_team_data.get("logo"),
                            description=away_team_data
                        )
                    #перенести/конец
                    season = event_data.get("season", {})
                    if season:
                        season_name = season.get("name")
                        season_id = season.get("id")

                    league = event_data.get("league", {})
                    if league:
                        league_name = league.get("name")
                        league_logo = league.get("logo")
                        league_slug = league.get("slug")
                        league_id = league.get("id")

                    existing_season = Season.objects.filter(slug=league_slug).first()
                    if existing_season:

                        league_slug = get_unique_season_slug(league_slug)

                    venue =  event_data.get("section", {})
                    if venue:
                        # слишком много запросов к API
                        country_name = venue.get("name")
                        country_name_ru = translate_to_russian(country_name)
                        try:
                            country_from_db = Country.objects.get(name=country_name_ru)
                        except:
                            country_from_db = Country.objects.create(name=country_name_ru)
                    try:
                        season_model=Season.objects.get(league_id=league_id,season_id=season_id)

                    except Season.DoesNotExist:
                        season_model = Season.objects.create(
                            rubrics=rubric,
                            season_name=season_name,
                            league_name=league_name,
                            description = event_data,
                            slug=league_slug,
                            league_id=league_id,
                            season_id=season_id,
                            logo_league=league_logo,
                            country = country_from_db
                        )
                    if not Events.objects.filter(event_api_id=event_data.get("id")).exists():
                        Events.objects.create(
                            rubrics = rubric,
                            event_api_id=event_data.get("id"),
                            name=event_data.get("name"),
                            description=json.dumps(event_data),
                            title=event_data.get("name"),
                            start_at=event_data.get("start_at"),
                            home_team=home_team,
                            away_team=away_team,
                            section = season_model,)
                    count_event += 1
                    print('count_event---', count_event)


                print(f"Data for {date_str} and api_team_id {api_rubric_id} fetched successfully")
            else:
                print(f"Error fetching data for {date_str} and api_team_id {api_rubric_id}: {response}")
            current_date += timedelta(days=1)
    return {"response": "Data fetched successfully"}
    # return HttpResponse("Data fetched successfully")

@shared_task
def fetch_event_data():
    current_datetime = timezone.now()
    yesterday = current_datetime - timedelta(days=1)
    events = Events.objects.filter(
        Q(start_at=yesterday)
                         | Q(start_at=current_datetime.date())
    )
    base_url = "https://sportscore1.p.rapidapi.com/events/{}"
    for event in events:
        url = base_url.format(event.event_api_id)
        response = requests.get(url, headers=HEADER_FOR_FIRST_API)
        if event.rubrics.api_id != 2 :
            if response.status_code == 200:
                event_data = response.json()
                if event_data['data']['start_at'] != event.start_at:
                    # Обновите start_at и установите reschedule в True
                    event.start_at = event_data['data']['start_at']
                    event.reschedule = True
                status_of_event = event_data['data']['status']

                if status_of_event == "inprogress" :
                    home_score = event_data['data']['home_score']['current']
                    away_score = event_data['data']['away_score']['current']
                    event.home_score = int(home_score)
                    event.away_score = int(away_score)
                    status_more = event_data['data']['status_more']
                    event.half = status_more
                    periods_data = event_data['data']
                    for period_key, period_score in periods_data['home_score'].items():
                        if period_key.startswith("period_"):
                            period_number = int(period_key.split("_")[1])
                            period_home_score = period_score
                            period_away_score = periods_data['away_score'][period_key]
                            period, created = Periods.objects.update_or_create(
                                event_api_id=periods_data['id'],
                                period_number=period_number,
                                home_score = int(period_home_score),
                                away_score = int(period_away_score)
                            )
                            event.periods.add(period)
                    event.description =  event_data
                    event.save()
                    # перенести
                    base_url_statistic = "https://sportscore1.p.rapidapi.com/events/{}/statistics"
                    url_statistic = base_url_statistic.format(event.event_api_id)
                    time.sleep(1)
                    response_statistic = requests.get(url_statistic, headers=HEADER_FOR_FIRST_API)
                    if response_statistic.status_code == 200:
                        statistics_data = response_statistic.json().get("data", [])
                        for statistic in statistics_data:
                            period = statistic.get("period", "all")
                            name = statistic.get("name").replace("_", " ").title()
                            t_name = translate_to_russian(name)
                            home = statistic.get("home", 0)
                            away = statistic.get("away", 0)
                            if period == '1st':
                                period_m = 1
                            elif period == '2nd':
                                period_m = 2
                            elif period == '3rd':
                                period_m = 3
                            elif period == '4th':
                                period_m = 4
                            elif period == '5th':
                                period_m = 5
                            else:
                                period_m = 6
                            if not GameStatistic.objects.filter(
                                    period=period_m,
                                    name=t_name,
                                    home=home,
                                    description=statistic,
                                    away=away
                            ).exists():
                                gs = GameStatistic.objects.create(
                                    period=period_m,
                                    name=t_name,
                                    home=home,
                                    description=statistic,
                                    away=away
                                )
                                event.statistic.add(gs)
                    else:
                        print(f"Error fetching data for event {event.event_api_id}: {response.json()}")
                    # перенести /конец
                    # перенести
                    base_url_incidents = "https://sportscore1.p.rapidapi.com/events/{}/incidents"
                    url_incidents = base_url_incidents.format(event.event_api_id)
                    time.sleep(1)
                    response = requests.get(url_incidents, headers=HEADER_FOR_FIRST_API)
                    if response.status_code == 200:
                        incident_data = response.json().get("data", [])
                        previous_incident_type = None

                        for incident in incident_data:
                            # Extract relevant data from the incident dictionary
                            incident_type = incident.get("incident_type")
                            player = incident.get("player")
                            player_team = incident.get("player_team")
                            description = incident
                            time_d = incident.get("time")
                            if incident_type == "card":
                                if player is not None:
                                    player_id = player.get("id")
                                    card_type = incident.get("card_type")
                                    try:
                                        player = Player.objects.get(player_id=player_id)
                                    except Player.DoesNotExist:
                                        base_url_player_data = "https://sportscore1.p.rapidapi.com/players/{}"
                                        url_player_data = base_url_player_data.format(player_id)
                                        response_for_player = requests.get(url_player_data, headers=HEADER_FOR_FIRST_API)
                                        if response_for_player.status_code == 200:
                                            player_data = response_for_player.json().get("data", [])
                                            player_id = player_data.get("id")
                                            slug = player_data.get("slug")
                                            name = player_data.get("name")
                                            photo = player_data.get("photo")
                                            position_name = player_data.get("position_name")
                                            player = Player.objects.create(
                                                player_id=player_id,
                                                slug=slug,
                                                name=name,
                                                photo=photo,
                                                position_name=position_name,
                                                main_player=True
                                            )
                                    if not Incidents.objects.filter(
                                            time=time_d,
                                            rubrics=event.rubrics,
                                            incident_type=incident_type,
                                            player=player,
                                            player_team=player_team,
                                            description=description,
                                            card_type=card_type
                                    ).exists():
                                        incident = Incidents.objects.create(
                                            time=time_d,
                                            rubrics=event.rubrics,
                                            incident_type=incident_type,
                                            player=player,
                                            player_team=player_team,
                                            description=description,
                                            card_type=card_type
                                        )
                                        event.incidents.add(incident)
                                else:
                                    pass
                            elif incident_type == "goal":
                                if player is not None:
                                    player_id = player.get("id")
                                    scoring_team = incident.get("scoring_team")
                                    try:
                                        player = Player.objects.get(player_id=player_id)
                                    except Player.DoesNotExist:
                                        base_url_player_data = "https://sportscore1.p.rapidapi.com/players/{}"
                                        url_player_data = base_url_player_data.format(player_id)
                                        time.sleep(1)
                                        response_for_player = requests.get(url_player_data, headers=HEADER_FOR_FIRST_API)
                                        if response_for_player.status_code == 200:
                                            player_data = response_for_player.json().get("data", [])
                                            player_id = player_data.get("id")
                                            slug = player_data.get("slug")
                                            name = player_data.get("name")
                                            photo = player_data.get("photo")
                                            shirt_num = player_data.get("shirt_number")
                                            rating = player_data.get("rating")
                                            position_name = player_data.get("position_name")
                                            i = 1
                                            while Player.objects.filter(slug=slug).exists():
                                                slug = f"{player_data.get('slug')}{i}"
                                                i += 1

                                            player = Player.objects.create(
                                                player_id=player_id,
                                                slug=slug,
                                                name=name,
                                                photo=photo,
                                                position_name=position_name,
                                                main_player=True,
                                                number=shirt_num,
                                                reiting=rating
                                            )
                                    if not Incidents.objects.filter(
                                            time=time_d,
                                            scoring_team=scoring_team,
                                            rubrics=event.rubrics,
                                            incident_type=incident_type,
                                            player=player,
                                            player_team=player_team,
                                            description=description,
                                    ).exists():
                                        incident = Incidents.objects.create(
                                            time=time_d,
                                            scoring_team=scoring_team,
                                            rubrics=event.rubrics,
                                            incident_type=incident_type,
                                            player=player,
                                            player_team=player_team,
                                            description=description,
                                        )
                                        event.incidents.add(incident)
                                else:
                                    pass
                            elif incident_type == "substitution":
                                if player is not None:
                                    player_id = player.get("id")
                                    player_two = incident.get("player_two_in")
                                    player_two_id = player_two.get("id")
                                    try:
                                        player_two_in = Player.objects.get(player_id=player_two_id)
                                    except Player.DoesNotExist:
                                        base_url_player_data = "https://sportscore1.p.rapidapi.com/players/{}"
                                        url_player_data = base_url_player_data.format(player_two_id)
                                        response_for_player = requests.get(url_player_data, headers=HEADER_FOR_FIRST_API)
                                        time.sleep(1)
                                        if response_for_player.status_code == 200:
                                            player_data = response_for_player.json().get("data", [])
                                            player_id = player_data.get("id")
                                            slug = player_data.get("slug")
                                            name = player_data.get("name")
                                            photo = player_data.get("photo")
                                            position_name = player_data.get("position_name")
                                            player_two_in = Player.objects.create(
                                                player_id=player_id,
                                                slug=slug,
                                                name=name,
                                                photo=photo,
                                                position_name=position_name,
                                                main_player=True
                                            )
                                    try:
                                        player = Player.objects.get(player_id=player_id)
                                    except Player.DoesNotExist:
                                        base_url_player_data = "https://sportscore1.p.rapidapi.com/players/{}"
                                        url_player_data = base_url_player_data.format(player_id)
                                        time.sleep(1)
                                        response_for_player = requests.get(url_player_data, headers=HEADER_FOR_FIRST_API)
                                        if response_for_player.status_code == 200:
                                            player_data = response_for_player.json().get("data", [])
                                            player_id = player_data.get("id")
                                            slug = player_data.get("slug")
                                            name = player_data.get("name")
                                            photo = player_data.get("photo")
                                            position_name = player_data.get("position_name")
                                            player = Player.objects.create(
                                                player_id=player_id,
                                                slug=slug,
                                                name=name,
                                                photo=photo,
                                                position_name=position_name,
                                                main_player=True
                                            )
                                    if not Incidents.objects.filter(
                                            time=time_d,
                                            rubrics=event.rubrics,
                                            incident_type=incident_type,
                                            player=player,
                                            player_two_in=player_two_in,
                                            player_team=player_team,
                                            description=description,
                                    ).exists():
                                        incident = Incidents.objects.create(
                                            time=time_d,
                                            rubrics=event.rubrics,
                                            incident_type=incident_type,
                                            player=player,
                                            player_two_in=player_two_in,
                                            player_team=player_team,
                                            description=description,
                                        )
                                        event.incidents.add(incident)
                                else:
                                    pass
                            elif incident_type == "injuryTime":
                                inj_time = incident.get("text")
                                match = re.search(r'\d+', inj_time)
                                if match:
                                    inj_time_ot = match.group()
                                else:
                                    inj_time_ot = ''
                                if not Incidents.objects.filter(
                                        rubrics=event.rubrics,
                                        incident_type=incident_type,
                                        description=description,
                                        time=time_d,
                                        inj_time=inj_time_ot
                                ).exists():
                                    incident = Incidents.objects.create(
                                        rubrics=event.rubrics,
                                        incident_type=incident_type,
                                        description=description,
                                        time=time_d,
                                        inj_time=inj_time_ot
                                    )
                                    event.incidents.add(incident)
                            else:
                                if not Incidents.objects.filter(
                                        rubrics=event.rubrics,
                                        incident_type=incident_type,
                                        description=description,
                                        time=time_d,
                                ).exists():
                                    incident = Incidents.objects.create(
                                        rubrics=event.rubrics,
                                        incident_type=incident_type,
                                        description=description,
                                        time=time_d,
                                    )
                                    event.incidents.add(incident)
                                incidents = event.incidents.all()
                                for i in range(1, len(incidents)):
                                    current_incident = incidents[i]
                                    previous_incident = incidents[i - 1]
                                    if current_incident.incident_type == 'period' and previous_incident.incident_type == 'period':
                                        previous_incident.delete()
                    # перенести/конец
                if status_of_event == "finished":
                    event.status = 2
                elif status_of_event == "inprogress":
                    event.status = 1
                elif status_of_event == 'canceled':
                    event.status = 4
            else:
                print(f"Error fetching data for event {event.event_api_id}: {response.json()}")

        if event.rubrics.api_id ==2 :
            # перенести
            base_tennis_point_url = "https://sportscore1.p.rapidapi.com/events/{}/points"
            tennis_point_url = base_tennis_point_url.format(event.event_api_id)
            response_tennis_point = requests.get(tennis_point_url, headers=HEADER_FOR_FIRST_API)
            if response_tennis_point.status_code == 200:
                tennis_point_data = response_tennis_point.json().get("data", [])
                if tennis_point_data:
                    for item in tennis_point_data:
                        event_id = item.get("id")
                        point_type = item.get("type", [])
                        for type in point_type:
                            set = type.get("set")
                            tp = TennisPoints.objects.create(
                                set = set,
                                api_id_tp = event_id
                            )
                            games = type.get("games", [])
                            for game in games:
                                points = game.get("points", [])
                                score = game.get("score", [])
                                game_d = game.get("game")
                                if score:
                                    serving = score.get("serving")
                                    homeScore = score.get("homeScore")
                                    awayScore = score.get("awayScore")
                                    try :
                                        tg = TennisGames.objects.get(
                                            game=game_d,
                                            home_score=homeScore,
                                            away_score=awayScore,
                                            serving=serving
                                        )
                                    except:
                                        tg = TennisGames.objects.create(
                                            game = game_d,
                                            home_score = homeScore,
                                            away_score = awayScore,
                                            serving = serving
                                        )

                                    for point in points:
                                        homePoint = point.get("homePoint")
                                        awayPoint = point.get("awayPoint")
                                        points = Points.objects.create(
                                            homePoint = homePoint,
                                            awayPoint = awayPoint
                                        )
                                        tg.points.add(points)
                                        tp.games.add(tg)
                                event.tennis_points.add(tp)
            # перенести/конец
    # return HttpResponse("Data fetched successfully")
    return {"response": "Data fetched successfully"}


@shared_task
def get_players_in_team():
    # перенести
    base_url_team = "https://sportscore1.p.rapidapi.com/teams/{}/players"

    querystring = {"page": "1"}
    teams =Team.objects.filter(players=None)
    for team in teams:
        url_team = base_url_team.format(team.api_team_id)

        response_players_in_team = requests.get(url_team, headers=HEADER_FOR_FIRST_API, params=querystring)
        if response_players_in_team.status_code == 200:
            players_r = response_players_in_team.json().get("data", [])
            count = 0
            for player in players_r:
                try:
                    player = Player.objects.get(player_id=player["id"])

                except Player.DoesNotExist:
                    if count < 11:
                        player = Player.objects.create(
                            player_id=player["id"],
                            slug=player["slug"],
                            name=player["name"],
                            photo=player["photo"],
                            position_name=player["position"],
                            description=player,
                            main_player=True,
                            reiting=player["rating"],
                            number=player["shirt_number"],
                        )
                    else:
                        player = Player.objects.create(
                            player_id=player["id"],
                            slug=player["slug"],
                            name=player["name"],
                            photo=player["photo"],
                            position_name=player["position"],
                            description=player,
                            main_player=False,
                            reiting=player["rating"],
                            number=player["shirt_number"],
                        )
                team.players.add(player)
                count += 1
    # return HttpResponse("Data fetched successfully")
    return {"response": "Data fetched successfully"}


@shared_task
def get_h2h():
    events = Events.objects.filter(status=3)
    for event in events:
        home_team = event.home_team.api_team_id
        away_team = event.away_team.api_team_id

        base_events_bytTID_url = "https://sportscore1.p.rapidapi.com/teams/{}/h2h-events/{}"
        events_bytTID_url = base_events_bytTID_url.format(home_team,away_team)
        querystring = {"page": "1"}

        response_for_events_bytTID = requests.get(events_bytTID_url, headers=HEADER_FOR_FIRST_API,
                                                  params=querystring)
        if response_for_events_bytTID.status_code == 200:
            data_events_TID = response_for_events_bytTID.json().get("data", [])
            for item in data_events_TID:
                status_of_game = item.get("status")
                if status_of_game == 'finished':
                    home_team_d = item.get("home_team")
                    away_team_d = item.get("away_team")
                    home_team_id = home_team_d.get("id")
                    away_team_id = away_team_d.get("id")
                    h2h_base_url = "https://sportscore1.p.rapidapi.com/teams/{}/h2h-events/{}"
                    querystring = {"page": "1"}
                    h2h_url = h2h_base_url.format(home_team_id, away_team_id)
                    response_h2h = requests.get(h2h_url, headers=HEADER_FOR_FIRST_API, params=querystring)
                    if response_h2h.status_code == 200:
                        h2h_data = response_h2h.json().get("data", [])
                        for h2hdata in h2h_data:
                            status = h2hdata.get("status")
                            league = h2hdata.get("league")
                            away_score = h2hdata.get("away_score")
                            home_score = h2hdata.get("home_score")
                            if status == 'finished' and league is not None and home_score is not None and away_score is not None:
                                try:
                                    h2h_stat = H2H.objects.get(api_h2h_id=h2hdata.get("id"))
                                except:
                                    h2h_stat = H2H.objects.create(
                                        api_h2h_id=h2hdata.get("id"),
                                        home_score=h2hdata.get("home_score").get("current"),
                                        away_score=h2hdata.get("away_score").get("current"),
                                        name=h2hdata.get("name", ""),
                                        home_team_ID=h2hdata.get("home_team").get("id"),
                                        away_team_ID=h2hdata.get("away_team").get("id"),
                                        home_team_NAME=h2hdata.get("home_team").get("name"),
                                        home_team_LOGO=h2hdata.get("home_team").get("logo"),
                                        away_team_NAME=h2hdata.get("away_team").get("name"),
                                        away_team_LOGO=h2hdata.get("away_team").get("logo"),
                                        league=h2hdata.get("league").get("name"),
                                        league_logo=h2hdata.get("league").get("logo"),
                                        start_at=h2hdata.get("start_at")
                                    )
                                event.h2h.add(h2h_stat)
                            else:
                                pass
    # return HttpResponse("Data fetched successfully")
    return {"response": "Data fetched successfully"}


#Вторая апи
@shared_task
def add_sport_events_list_second():
    second_url = "https://flashlive-sports.p.rapidapi.com/v1/events/list"

    base_querystring = {"timezone": "-4", "indent_days": "-1", "locale": "ru_RU", "sport_id": ""}
    second_api_rubric_ids = Rubrics.objects.filter(second_api=True).values_list("api_id", flat=True).distinct()

    for rubric_id in second_api_rubric_ids:
        rubric_id_q = str(rubric_id)
        querystring = {"timezone": "-4", "indent_days": "7", "locale": "ru_RU", "sport_id": rubric_id_q}
        rubrics = Rubrics.objects.get(second_api=True, api_id=rubric_id)
        second_response = requests.get(second_url, headers=HEADER_FOR_SECOND_API, params=querystring)
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
                    country_from_db, created = Country.objects.get_or_create(name=event_data.get("COUNTRY_NAME"))
                    season = Season.objects.create(
                        rubrics=rubrics,
                        season_second_api_id=event_data.get("TOURNAMENT_SEASON_ID"),
                        season_name=event_data.get("NAME"),
                        logo_league=event_data.get("TOURNAMENT_IMAGE"),
                        country=country_from_db,
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
    #         return HttpResponse(f"Error  - {second_response.status_code} - {second_response.json()}")
    # return HttpResponse("Data fetched successfully")
            return {"response": f"Error  - {second_response.status_code} - {second_response.json()}"}
        return {"response": "Data fetched successfully"}

@shared_task
def add_sport_events_list_second_online_gou():
    second_url = "https://flashlive-sports.p.rapidapi.com/v1/events/live-list"

    second_api_rubric_ids = Rubrics.objects.filter(second_api=True).values_list("api_id", flat=True).distinct()
    # это логи ?
    # with open('/var/www/chester/add_sport_events_list_second_online_gou.txt', 'w') as file:
    #     file.write('its works\n')
    for rubric_id in second_api_rubric_ids:
        rubric_id_q = str(rubric_id)
        querystring = {"timezone": "-4", "locale": "ru_RU", "sport_id": rubric_id_q}


        rubrics = Rubrics.objects.get(second_api=True, api_id=rubric_id)
        second_response = requests.get(second_url, headers=HEADER_FOR_SECOND_API, params=querystring)
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
    #         return HttpResponse(f"Error  - {second_response.status_code} - {second_response.json()}")
    #
    # return HttpResponse("Data fetched successfully")
            return {"response": f"Error  - {second_response.status_code} - {second_response.json()}"}
        return {"response": "Data fetched successfully"}

@shared_task
def fetch_event_data_for_second():
    events = Events.objects.filter(second_event_api_id__isnull=False)
    url = "https://flashlive-sports.p.rapidapi.com/v1/events/data"

    # это логи ?
    # with open('/var/www/chester/fetch_event_data_for_second.txt', 'w') as file:
    #     file.write('its works\n')
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
        second_url = "https://flashlive-sports.p.rapidapi.com/v1/events/h2h"

        second_querystring = {"locale": "en_INT", "event_id": event.second_event_api_id}

        second_response = requests.get(second_url, headers=HEADER_FOR_SECOND_API, params=second_querystring)
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
    return {"response": "Data fetched successfully"}
    # return HttpResponse("Data fetched successfully")

@shared_task
def get_team_players_second():
    url = "https://flashlive-sports.p.rapidapi.com/v1/events/lineups"
    events = Events.objects.filter(second_event_api_id__isnull = False ,status=1)
    for event in events:
        querystring = {"locale": "ru_RU", "event_id": event.second_event_api_id}
        response = requests.get(url, headers=HEADER_FOR_SECOND_API, params=querystring)
        if response.status_code == 200:
            count = 0
            response_data = response.json().get("DATA")
            for data in response_data:
                formation_name = data.get("FORMATION_NAME")
                formations = data.get("FORMATIONS",[])
                for formation in formations:
                    members = formation.get("MEMBERS",[])
                    for player in members:
                        try:
                            player = Player.objects.get(player_id=player["id"])
                        except Player.DoesNotExist:
                            if count < 1:
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
                                else :
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
                            elif count == 1 :
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
                    count += 1
    return {"response": "Data fetched successfully"}
    #
    # return HttpResponse("Data "
    #                     "fetched successfully")

@shared_task
def get_h2h_second():

    events = Events.objects.filter(second_event_api_id__isnull = False)
    for event in events:
        second_url = "https://flashlive-sports.p.rapidapi.com/v1/events/h2h"
        second_querystring = {"locale": "en_INT", "event_id": event.second_event_api_id}
        # H2H события
        second_response = requests.get(second_url, headers=HEADER_FOR_SECOND_API, params=second_querystring)
        if second_response.status_code == 200:
            second_response_data = second_response.json().get("DATA", [])
            for el in second_response_data:
                groups = el.get("GROUPS")
                for group in groups:
                    print('----group-----', group)
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
                                    start_at=datetime.utcfromtimestamp(item.get('START_TIME')),
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
                                    start_at=datetime.utcfromtimestamp(item.get('START_TIME')),
                                    h_result=item.get("H_RESULT"),
                                    team_mark=item.get("TEAM_MARK"),
                                )
                                event.h2h.add(h2h)
    # return HttpResponse("Data fetched successfully")
    return {"response": "Data fetched successfully"}

