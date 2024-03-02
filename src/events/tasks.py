from celery import shared_task
import requests
from datetime import datetime, timedelta
from .models import Rubrics, Season, Team, Events, H2H, Country, TimePeriod
from django.db.models import Q, Count
from events.models import Rubrics, Events, Team, Season, Player, Incidents, Periods, GameStatistic, H2H, TennisPoints, \
    TennisGames, Points, Country, Stages, IncidentParticipants
from django.utils.text import slugify
from googletrans import Translator
import time
from mainapp.models import GeneralSettings


general_settings = GeneralSettings.objects.first()
MAX_RETRIES = 2
HEADER_FOR_SECOND_API =  {
    'X-RapidAPI-Key': str(general_settings.rapidapi_key_events),
    "X-RapidAPI-Host": "flashlive-sports.p.rapidapi.com"
    }

HEADER_FOR_LIVE_STREAM = {
    'X-RapidAPI-Key': str(general_settings.rapidapi_key_stream),
    "X-RapidAPI-Host": "free-football-soccer-videos.p.rapidapi.com"
    }

EVENT_STATUSES = {
    'LIVE': 1,
    'FINISHED': 2,
    'SCHEDULED': 3
}


def generate_event_slug(home_team, away_team, start_at):
    # Создаем slug из полей home_team, away_team и start_at
    slug_text = f'{home_team}+{away_team}+{start_at}'

    # Заменяем пробелы на тире
    slug_text = slug_text.replace(' ', '-')

    # Словарь для замены русских букв на английские
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '',
        'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }

    # Преобразуем текст, заменяя русские буквы на английские
    slug_text = ''.join(translit_dict.get(c.lower(), c) for c in slug_text)

    # Преобразуем текст в slug
    return f'smotret-online-{slugify(slug_text)}'


# done optimization
# @shared_task
# def clear_dublicate_events():
#     duplicate_ids = Events.objects.values('second_event_api_id').annotate(count=Count('second_event_api_id')).filter(
#         count__gt=1)
#     count = 0
#     # Оставляем один объект с каждым значением second_event_api_id
#     for duplicate_id in duplicate_ids:
#         # Получаем первый объект с заданным second_event_api_id
#         keep_event = Events.objects.filter(second_event_api_id=duplicate_id['second_event_api_id']).first()
#         # Получаем все объекты, кроме первого
#         delete_events = Events.objects.filter(second_event_api_id=duplicate_id['second_event_api_id']).exclude(
#             id=keep_event.id)
#         # Удаляем все объекты, кроме первого
#         delete_events.delete()
#         count +=1
#     return {"response": f"Одинаковые события удалены - кол-во = {count} "}


@shared_task
def create_tournament():
    tournaments_list_url = "https://flashlive-sports.p.rapidapi.com/v1/tournaments/list"
    ids = [1, 2, 3, 4, 6, 7, 12, 13, 15, 21, 25, 36]
    for locale in ["ru_RU", "en_INT"]:
        for rubric_id in ids:
            rubric_id_q = str(rubric_id)
            querystring_tournaments_list = {"sport_id": rubric_id_q, "locale": locale }
            rubrics = Rubrics.objects.get(api_id=rubric_id)
            response_tournaments_list = requests.get(
                tournaments_list_url,
                headers=HEADER_FOR_SECOND_API,
                params=querystring_tournaments_list
            )
            if response_tournaments_list.status_code == 200:
                tournaments_data = response_tournaments_list.json()
                for tournament_data in tournaments_data.get("DATA", []):
                    country_name = tournament_data.get('COUNTRY_NAME','' )
                    if not country_name:
                        country_name = 'Мир'
                    if Country.objects.filter(name=country_name).exists():
                        country = Country.objects.filter(name=country_name).first()
                    elif Country.objects.filter(name_en=country_name).exists():
                        country = Country.objects.filter(name_en=country_name).first()
                    else:
                        country = Country.objects.create(name=country_name , name_en=country_name)
                    season_id = tournament_data.get("ACTUAL_TOURNAMENT_SEASON_ID")

                    if  Season.objects.filter(rubrics=rubrics,season_id=season_id,league_name= tournament_data.get("LEAGUE_NAME"),country= country).exists():
                        season = Season.objects.filter(rubrics=rubrics,season_id=season_id,league_name= tournament_data.get("LEAGUE_NAME"),country= country).first()
                    else:
                        season = Season.objects.create(rubrics=rubrics, season_id=season_id,league_name=tournament_data.get("LEAGUE_NAME"), country=country)

                    stages = tournament_data.get("STAGES")
                    stages_list = []
                    for stage in stages:
                        stage_id = stage.get("STAGE_ID")
                        stage_name = stage.get("STAGE_NAME")
                        stage_db = Stages(
                            stage_id=stage_id
                        )
                        if stage_name:
                            stage_db.stage_name = stage_name
                        stages_list.append(stage_db)
                    stages = Stages.objects.bulk_create(stages_list)
                    season.stages.add(*stages)
            else:
                return {
                    "response": f"Error  - {response_tournaments_list.status_code} - {response_tournaments_list.json()}"}

    return {"response": "create_tournament successfully"}


def create_events_of_tournament(rubric_id):
    second_url = "https://flashlive-sports.p.rapidapi.com/v1/tournaments/fixtures"
    rubrics = Rubrics.objects.get(
        api_id=rubric_id
    )
    seasons = Season.objects.filter(rubrics=rubrics)
    for locale in ["en_INT","ru_RU" ]:
        for season in seasons:
            stages = season.stages.all()
            for stage in stages:
                page = 1
                while True:
                    querystring = {"locale": locale, "tournament_stage_id": str(stage.stage_id), "page": str(page)}

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
                                if Country.objects.filter(name=event_data.get("COUNTRY_NAME")).exists():
                                    country_from_db = Country.objects.filter(name=event_data.get("COUNTRY_NAME")).first()
                                elif Country.objects.filter(name_en=event_data.get("COUNTRY_NAME")).exists():
                                    country_from_db =  Country.objects.filter(name_en=event_data.get("COUNTRY_NAME")).first()
                                else:
                                    country_from_db = Country.objects.create(name=event_data.get("COUNTRY_NAME"),name_en=event_data.get("COUNTRY_NAME"))
                            if Season.objects.filter(rubrics=rubrics,season_id=event_data.get("TOURNAMENT_SEASON_ID")).exists():
                                season = Season.objects.filter(rubrics=rubrics,season_id=event_data.get("TOURNAMENT_SEASON_ID")).first()
                            else:
                                season = Season.objects.create(rubrics=rubrics,season_id=event_data.get("TOURNAMENT_SEASON_ID"))
                                season.country = country_from_db
                                season.season_second_api_id = event_data.get("TOURNAMENT_STAGE_ID")

                            season.logo_league = correct_logo_season
                            season.season_name = event_data.get("NAME")
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

                                    if Team.objects.filter(second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1]).exists():
                                        home_team = Team.objects.filter(second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1]).first()
                                    else:
                                        home_team = Team.objects.create(
                                            second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1],
                                            name=event.get("HOME_NAME"),
                                            logo=correct_home_logo,
                                            rubrics=rubrics
                                        )

                                    if Team.objects.filter(second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1]).exists():
                                        away_team = Team.objects.filter(second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1]).first()
                                    else:
                                        away_team = Team.objects.create(
                                        second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1],
                                        name = event.get("AWAY_NAME"),
                                        logo = correct_away_logo,
                                        rubrics = rubrics
                                        )
                                    if not Events.objects.filter(rubrics=rubrics, second_event_api_id=event.get("EVENT_ID")).exists():
                                        events_list.append(Events(
                                            rubrics=rubrics,
                                            second_event_api_id=event.get("EVENT_ID"),
                                            start_at=datetime.utcfromtimestamp(event.get("START_TIME")),
                                            name=event_data.get("NAME_PART_2"),
                                            title=event_data.get("SHORT_NAME"),
                                            status=status_id,
                                            home_team=home_team,
                                            away_team=away_team,
                                            home_score=event.get("HOME_SCORE_CURRENT"),
                                            away_score=event.get("AWAY_SCORE_CURRENT"),
                                            half=event.get("ROUND"),
                                            section=season,
                                            slug = generate_event_slug(event.get("HOME_NAME"),event.get("AWAY_NAME") ,datetime.utcfromtimestamp(event.get("START_TIME"))  ),
                                        ))
                            Events.objects.bulk_create(events_list)
                        page += 1
                    elif second_response.status_code == 404:
                        try:
                            stage.delete()
                        except:
                            pass
                        break
                    else:
                        break
                try:
                    stage.delete()
                except:
                    pass
    return {"response": "create_events_of_tournament successfully"}


@shared_task
def create_events_of_tournament_id1():
    return create_events_of_tournament(1)



@shared_task
def create_events_of_tournament_id2():
    return create_events_of_tournament(2)


@shared_task
def create_events_of_tournament_id3():
    return create_events_of_tournament(3)


@shared_task
def create_events_of_tournament_id4():
    return create_events_of_tournament(4)


@shared_task
def create_events_of_tournament_id6():
    return create_events_of_tournament(6)


@shared_task
def create_events_of_tournament_id7():
    return create_events_of_tournament(7)


@shared_task
def create_events_of_tournament_id12():
    return create_events_of_tournament(12)


@shared_task
def create_events_of_tournament_id13():
    return create_events_of_tournament(13)


@shared_task
def create_events_of_tournament_id15():
    return create_events_of_tournament(15)


@shared_task
def create_events_of_tournament_id21():
    return create_events_of_tournament(21)


@shared_task
def create_events_of_tournament_id25():
    return create_events_of_tournament(25)


@shared_task
def create_events_of_tournament_id36():
    return create_events_of_tournament(36)


def fetch_event_data(rubric_id):
    incidents_url = "https://flashlive-sports.p.rapidapi.com/v1/events/summary-incidents"

    rubrics = Rubrics.objects.get(
        api_id=rubric_id
    )
    incidents_events = Events.objects.filter(status=1, rubrics=rubrics)

    # incidents
    for event in incidents_events:
        retries = 0
        while retries < MAX_RETRIES:
            incidents_response = requests.get(
                incidents_url,
                headers=HEADER_FOR_SECOND_API,
                params={"locale": "ru_RU", "event_id": event.second_event_api_id}
            )
            if incidents_response.status_code == 200:
                incidents_response_data = incidents_response.json().get("DATA", [])
                for data in incidents_response_data:
                    fields = {
                        "home_score": data.get('RESULT_HOME', 0),
                        "away_score": data.get('RESULT_AWAY', 0)
                    }
                    period, created = Periods.objects.get_or_create(
                        period_number=data.get('STAGE_NAME', 0),
                        event_api_id=event.second_event_api_id,
                        defaults=fields
                    )
                    if not created:
                        for field, value in fields.items():
                            if getattr(period, field) != value:
                                setattr(period, field, value)
                    period.save()
                    event.periods.add(period)
                    event.save()
                    data_items = data.get("ITEMS", [])
                    for item in data_items:
                        incident, created = event.incidents.get_or_create(
                            incident_api_id=item.get('INCIDENT_ID'),
                            rubrics=rubrics,
                            defaults={
                                "incident_team": item.get('INCIDENT_TEAM'),
                                "time": item.get('INCIDENT_TIME', '0')
                            }
                        )
                        incident_participants_objs = []
                        for participant in item.get('INCIDENT_PARTICIPANTS', []):
                            try:
                                incident_participant, created = IncidentParticipants.objects.get_or_create(
                                    participant_id=participant.get("PARTICIPANT_ID"),
                                    defaults={
                                        "incident_type": participant.get("INCIDENT_TYPE"),
                                        "participant_name": participant.get("PARTICIPANT_NAME"),
                                        "incident_name": participant.get("PARTICIPANT_NAME"),
                                    }
                                )
                                incident_participants_objs.append(incident_participant)
                            except:
                                pass
                        incident.incident_participants.add(*incident_participants_objs)
                        incident.save()
                        event.incidents.add(incident)
                        event.save()
                break
            elif incidents_response.status_code == 429:
                retries += 1
                if retries < MAX_RETRIES:
                    if retries == MAX_RETRIES:
                        pass
                    time.sleep(2)
                    continue
                else:
                    pass

    return {"response": f"fetch_event_data_for_second successfully"}
def get_statistic_event(rubric_id):
    rubrics = Rubrics.objects.get(
        api_id=rubric_id
    )
    statistics_url = "https://flashlive-sports.p.rapidapi.com/v1/events/statistics"
    gamestatistic_events = Events.objects.filter(status=1, rubrics=rubrics)
    # gamestatistic
    for event in gamestatistic_events:
        retries = 0
        while retries < MAX_RETRIES:
            gamestatistic_response = requests.get(
                statistics_url,
                headers=HEADER_FOR_SECOND_API,
                params={
                    "locale": "ru_RU",
                    "event_id": event.second_event_api_id}
            )
            if gamestatistic_response.status_code == 200:
                gamestatistic_response_data = gamestatistic_response.json().get("DATA", [])
                for data in gamestatistic_response_data:
                    stage_name = data.get("STAGE_NAME", 0)
                    groups = data.get("GROUPS")
                    for group in groups:
                        items = group.get("ITEMS", [])
                        for item in items:
                            incident_name = item.get("INCIDENT_NAME")
                            value_home = item.get("VALUE_HOME")
                            value_away = item.get("VALUE_AWAY")
                            if event.statistic.filter(name=incident_name).exists():
                                gamestatistic = event.statistic.filter(name=incident_name).first()
                                gamestatistic.period = stage_name
                                gamestatistic.home = value_home
                                gamestatistic.away = value_away
                                gamestatistic.save()

                            if event.statistic.filter(period=stage_name, name=incident_name, home=value_home,
                                                      away=value_away).exists():
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
                break
            elif gamestatistic_response.status_code == 429:
                retries += 1
                if retries < MAX_RETRIES:
                    if retries == MAX_RETRIES:
                        pass
                    time.sleep(3)
                    continue
                else:
                    pass

    return {"response": f"get_statistic_event successfully"}
@shared_task
def get_statistic_event_id1():
    return get_statistic_event(1)
@shared_task
def get_statistic_event_id2():
    return get_statistic_event(2)
@shared_task
def get_statistic_event_id3():
    return get_statistic_event(3)
@shared_task
def get_statistic_event_id4():
    return get_statistic_event(4)
@shared_task
def get_statistic_event_id6():
    return get_statistic_event(6)
@shared_task
def get_statistic_event_id7():
    return get_statistic_event(7)
@shared_task
def get_statistic_event_id12():
    return get_statistic_event(12)
@shared_task
def get_statistic_event_id13():
    return get_statistic_event(13)
@shared_task
def get_statistic_event_id15():
    return get_statistic_event(15)
@shared_task
def get_statistic_event_id21():
    return get_statistic_event(21)
@shared_task
def get_statistic_event_id25():
    return get_statistic_event(25)
@shared_task
def get_statistic_event_id36():
    return get_statistic_event(36)


#события на затрва (нужны тк таска отправляет запрос но не получает некоторые матчи ,проблема апи)
def update_event_data(sport_id):
    url = "https://flashlive-sports.p.rapidapi.com/v1/events/list"
    rubrics = Rubrics.objects.get(
        api_id=sport_id
    )
    event_ids = []
    for locale in ["en_INT", "ru_RU"]:
        retries = 0
        querystring = {"indent_days": "0", "timezone": "-4", "locale": locale, "sport_id": str(sport_id)}
        while retries < MAX_RETRIES:
            response = requests.get(url, headers=HEADER_FOR_SECOND_API, params=querystring)
            if response.status_code == 200:
                response_data = response.json().get("DATA")
                for league in response_data:
                    league_name = league.get("NAME","")
                    country_name =league.get("COUNTRY_NAME","Мир")
                    tournament_image =league.get("TOURNAMENT_IMAGE","")
                    if tournament_image:
                        normal_ti = tournament_image.replace('www.', 'static.')
                    tournament_id =league.get("TOURNAMENT_SEASON_ID","")

                    events = league.get("EVENTS")
                    if Country.objects.filter(name=country_name).exists():
                        country =Country.objects.filter(name=country_name).first()
                    else:
                        country = Country.objects.create(name=country_name)
                    if Season.objects.filter(season_id=tournament_id).exists():
                        season = Season.objects.filter(season_id=tournament_id).first()
                    else:
                        season = Season.objects.create(rubrics=rubrics, season_id=tournament_id, league_name=league_name, country=country , logo_league = normal_ti)

                    events_list = []
                    events_list_update = []
                    time_periods_to_create = []
                    time_periods_to_update = []
                    for event in events:
                        event_id = event.get('EVENT_ID')
                        if event_id:
                            event_ids.append(event_id)
                        homeimg_base = event.get("HOME_IMAGES")
                        awayimg_base = event.get("AWAY_IMAGES")
                        status_id = EVENT_STATUSES[event.get("STAGE_TYPE")]
                        correct_home_logo = ''
                        correct_away_logo = ''
                        if homeimg_base is not None and awayimg_base is not None:
                            logo_home = event.get("HOME_IMAGES")[-1]
                            if logo_home:
                                correct_home_logo = logo_home.replace('www.', 'static.')
                            logo_away = event.get("AWAY_IMAGES")[-1]
                            if logo_away:
                                correct_away_logo = logo_away.replace('www.', 'static.')

                        if Team.objects.filter(second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1]).exists():
                            home_team = Team.objects.filter(
                                second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1]).first()
                        else:
                            home_team = Team.objects.create(
                                second_api_team_id=event.get("HOME_PARTICIPANT_IDS")[-1],
                                name=event.get("HOME_NAME"),
                                logo=correct_home_logo,
                                rubrics=rubrics,
                            )

                        if Team.objects.filter(second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1]).exists():
                            away_team = Team.objects.filter(
                                second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1]).first()
                        else:
                            away_team = Team.objects.create(
                                second_api_team_id=event.get("AWAY_PARTICIPANT_IDS")[-1],
                                name=event.get("AWAY_NAME"),
                                logo=correct_away_logo,
                                rubrics=rubrics,
                            )
                        existing_event = Events.objects.filter(rubrics=rubrics,second_event_api_id=event.get("EVENT_ID")).first()

                        if existing_event is None:
                            stage = event.get("STAGE"),
                            new_event = Events(
                                rubrics=rubrics,
                                second_event_api_id=event.get("EVENT_ID"),
                                start_at=datetime.utcfromtimestamp(event.get("START_TIME")),
                                name=league_name,
                                title=league_name,
                                status=status_id,
                                home_team=home_team,
                                away_team=away_team,
                                home_score=event.get("HOME_SCORE_CURRENT"),
                                away_score=event.get("AWAY_SCORE_CURRENT"),
                                half=stage,
                                section=season,
                                slug=generate_event_slug(event.get("HOME_NAME"), event.get("AWAY_NAME"),
                                                         datetime.utcfromtimestamp(event.get("START_TIME"))),
                            )
                            if event.get("STAGE_START_TIME"):
                                start = datetime.utcfromtimestamp(event.get("STAGE_START_TIME"))
                                start_time = start.strftime('%H:%M:%S')
                                time_periods_to_create.append(TimePeriod(
                                    event=new_event,
                                    start=start_time
                                ))

                            events_list.append(new_event)
                        else:
                            stage =event.get("STAGE")
                            existing_event.home_score = event.get("HOME_SCORE_CURRENT")
                            existing_event.away_score = event.get("AWAY_SCORE_CURRENT")
                            existing_event.status = status_id
                            existing_event.start_at = datetime.utcfromtimestamp(event.get("START_TIME"))
                            start_time_fact = event.get("STAGE_START_TIME")
                            timeperiods = TimePeriod.objects.filter(event=existing_event)
                            if start_time_fact and not existing_event.start_at_for_timer:
                                existing_event.start_at_for_timer = datetime.utcfromtimestamp(start_time_fact)
                            if stage == 'HALF_TIME':
                                stage_time = datetime.utcfromtimestamp(event.get("STAGE_START_TIME"))
                                period_end_time = datetime.strptime(stage_time[-5:], '%H:%M')
                                formated_period_end_time = period_end_time.strftime('%H:%M:%S')
                                for periodtime in timeperiods:
                                    if not periodtime.end:
                                        periodtime.end = formated_period_end_time
                                        time_periods_to_update.append(periodtime)
                            if stage !='HALF_TIME' and existing_event.half == 'HALF_TIME' and stage != 'FINISHED':
                                stage_time = datetime.utcfromtimestamp(event.get("STAGE_START_TIME"))
                                period_end_pause_time = datetime.strptime(stage_time[-5:], '%H:%M')
                                formated_period_end_pause_time = period_end_pause_time.strftime('%H:%M:%S')
                                for periodtime in timeperiods:
                                    if not periodtime.end_pause:
                                        periodtime.end_pause = formated_period_end_pause_time
                                        time_periods_to_update.append(periodtime)
                                    else:
                                        time_periods_to_create.append(TimePeriod(event=existing_event,start= formated_period_end_pause_time))


                            existing_event.half = stage
                            events_list_update.append(existing_event)

                    Events.objects.bulk_create(events_list)
                    Events.objects.bulk_update(events_list_update, fields=[
                        'home_score', 'away_score', 'status','start_at','start_at_for_timer','time_half_time','half'
                    ])
                    TimePeriod.objects.bulk_create(time_periods_to_create)
                    TimePeriod.objects.bulk_update(time_periods_to_update, fields=['end', 'end_pause'])
                events_to_update = Events.objects.exclude(second_event_api_id__in=event_ids).filter(rubrics=rubrics,status=1)
                for event in events_to_update:
                    event.status = 2
                    event.save()

                break
            elif response.status_code == 429:
                retries += 1
                if retries < MAX_RETRIES:
                    if retries == MAX_RETRIES:
                        pass
                    time.sleep(1)
                    continue
                else:
                    pass
            else:
                pass

    return {"response": f"update_event_data ok"}

def create_h2h_and_players_for_new(sport_id):
    rubrics = Rubrics.objects.get(
        api_id=sport_id
    )
    # h2h в первый раз грузит если новый
    events_to_additional_info_h2h = Events.objects.filter(status=1,rubrics=rubrics,h2h_status=False)
    for event in events_to_additional_info_h2h:
        retries = 0
        while retries < MAX_RETRIES:
            response = requests.get(
                url="https://flashlive-sports.p.rapidapi.com/v1/events/h2h",
                headers=HEADER_FOR_SECOND_API,
                params={
                    "locale": "ru_RU",
                    "event_id": event.second_event_api_id
                }
            )
            if response.status_code == 200:
                second_response_data = response.json().get("DATA", [])
                for el in second_response_data:
                    groups = el.get("GROUPS")
                    for group in groups:
                        items = group.get("ITEMS", [])
                        for item in items:
                            hi = item.get("HOME_IMAGES")
                            ai = item.get("AWAY_IMAGES")
                            logo_away, logo_home = item.get("AWAY_IMAGES"), item.get("HOME_IMAGES")
                            if logo_away:
                                logo_away = logo_away[-1]
                                logo_away = logo_away.replace('www.', 'static.')
                            else:
                                logo_away = ''
                            if logo_home:
                                logo_home = logo_home[-1]
                                logo_home = logo_home.replace('www.', 'static.')
                            else:
                                logo_home = ''
                            if hi is not None and ai is not None:
                                h2h, created = H2H.objects.get_or_create(
                                    home_score=item.get("HOME_SCORE_FULL"),
                                    away_score=item.get("AWAY_SCORE_FULL"),
                                    name=item.get("EVENT_NAME"),
                                    home_team_NAME=item.get("HOME_PARTICIPANT"),
                                    home_team_LOGO=logo_home,
                                    away_team_NAME=item.get("AWAY_PARTICIPANT"),
                                    away_team_LOGO=logo_away,
                                    league=item.get("EVENT_NAME"),
                                    start_at=datetime.utcfromtimestamp(item.get("START_TIME")),
                                    h_result=item.get("H_RESULT"),
                                    team_mark=item.get("TEAM_MARK"),
                                )
                                event.h2h.add(h2h)
                                event.save()
                    event.h2h_status = True
                    event.save()
                break
            elif response.status_code == 429:
                retries += 1
                if retries < MAX_RETRIES:
                    if retries == MAX_RETRIES:
                        pass
                    time.sleep(1)
                    continue
                else:
                    pass
            else:
                pass
    # players в первый раз грузит если новый
    events_to_additional_info_players = Events.objects.filter(status=1, rubrics=rubrics,player_status=False)
    for event in events_to_additional_info_players:
        for locale in ["en_INT", "ru_RU"]:
            retries = 0
            while retries < MAX_RETRIES:
                response = requests.get(
                    url="https://flashlive-sports.p.rapidapi.com/v1/events/lineups",
                    headers=HEADER_FOR_SECOND_API,
                    params={
                        "locale": locale,
                        "event_id": event.second_event_api_id
                    }
                )
                if response.status_code == 200:
                    response_data = response.json().get("DATA")
                    for data in response_data:
                        formation_name = data.get("FORMATION_NAME")
                        formations = data.get("FORMATIONS", [])
                        for formation in formations:
                            team_line = formation.get("FORMATION_LINE")
                            if formation_name == 'Starting Lineups':
                                status_team_line = False
                            elif formation_name == 'Substitutes':
                                status_team_line = True
                            else:
                                status_team_line = False
                            members = formation.get("MEMBERS", [])
                            for player in members:
                                player_id = player.get("PLAYER_ID")
                                if player_id:
                                    fields = {
                                        "player_id": player_id,
                                        "slug": f'{player_id}',
                                        "name": player["PLAYER_FULL_NAME"],
                                        "position_name": player.get("PLAYER_POSITION"),
                                        "main_player": status_team_line,
                                        "number": player.get("PLAYER_NUMBER"),
                                        "photo": f'https://static.flashscore.com/res/image/data/{player.get("LPI")}'
                                    }
                                    player, created = Player.objects.get_or_create(
                                        slug=f'{player_id}'
                                    )
                                    for field, value in fields.items():
                                        if value:
                                            setattr(player, field, value)
                                    if not formation_name == 'Starting Lineups':
                                        setattr(player, "main_player", False)
                                    player.save()
                                    if team_line == 1:
                                        event.home_team.players.add(player)
                                    elif team_line == 2:
                                        event.away_team.players.add(player)
                                    event.player_status = True
                                    event.save()
                    break
                elif response.status_code == 429:
                    retries += 1
                    if retries < MAX_RETRIES:
                        if retries == MAX_RETRIES:
                            pass
                        time.sleep(1)
                        continue
                    else:
                        pass
                else:
                    pass

    return {"response": f"create_h2h_and_players_for_new ok"}
@shared_task
def create_h2h_and_players_for_new_id1():
    return create_h2h_and_players_for_new(1)

@shared_task
def create_h2h_and_players_for_new_id2():
    return create_h2h_and_players_for_new(2)

@shared_task
def create_h2h_and_players_for_new_id3():
    return create_h2h_and_players_for_new(3)

@shared_task
def create_h2h_and_players_for_new_id4():
    return create_h2h_and_players_for_new(4)

@shared_task
def create_h2h_and_players_for_new_id6():
    return create_h2h_and_players_for_new(6)

@shared_task
def create_h2h_and_players_for_new_id7():
    return create_h2h_and_players_for_new(7)

@shared_task
def create_h2h_and_players_for_new_id12():
    return create_h2h_and_players_for_new(12)

@shared_task
def create_h2h_and_players_for_new_id13():
    return create_h2h_and_players_for_new(13)

@shared_task
def create_h2h_and_players_for_new_id15():
    return create_h2h_and_players_for_new(15)

@shared_task
def create_h2h_and_players_for_new_id21():
    return create_h2h_and_players_for_new(21)

@shared_task
def create_h2h_and_players_for_new_id25():
    return create_h2h_and_players_for_new(25)

@shared_task
def create_h2h_and_players_for_new_id36():
    return create_h2h_and_players_for_new(36)

@shared_task
def update_event_data_id1():
    return update_event_data(1)

@shared_task
def update_event_data_id2():
    return update_event_data(2)

@shared_task
def update_event_data_id3():
    return update_event_data(3)

@shared_task
def update_event_data_id4():
    return update_event_data(4)

@shared_task
def update_event_data_id6():
    return update_event_data(6)

@shared_task
def update_event_data_id7():
    return update_event_data(7)

@shared_task
def update_event_data_id12():
    return update_event_data(12)

@shared_task
def update_event_data_id13():
    return update_event_data(13)

@shared_task
def update_event_data_id15():
    return update_event_data(15)

@shared_task
def update_event_data_id21():
    return update_event_data(21)

@shared_task
def update_event_data_id25():
    return update_event_data(25)

@shared_task
def update_event_data_id36():
    return update_event_data(36)

# обновление событий
@shared_task
def fetch_event_data_id1():
    return fetch_event_data(1)


@shared_task
def fetch_event_data_id2():
    return fetch_event_data(2)


@shared_task
def fetch_event_data_id3():
    return fetch_event_data(3)


@shared_task
def fetch_event_data_id4():
    return fetch_event_data(4)


@shared_task
def fetch_event_data_id6():
    return fetch_event_data(6)


@shared_task
def fetch_event_data_id7():
    return fetch_event_data(7)


@shared_task
def fetch_event_data_id12():
    return fetch_event_data(12)


@shared_task
def fetch_event_data_id13():
    return fetch_event_data(13)


@shared_task
def fetch_event_data_id15():
    return fetch_event_data(15)


@shared_task
def fetch_event_data_id21():
    return fetch_event_data(21)


@shared_task
def fetch_event_data_id25():
    return fetch_event_data(25)


@shared_task
def fetch_event_data_id36():
    return fetch_event_data(36)


@shared_task
def get_match_stream_link(rubric_id):
    rubrics = Rubrics.objects.get(
        api_id=rubric_id
    )

    url = "https://flashlive-sports.p.rapidapi.com/v1/events/highlights"
    events = Events.objects.filter(status=1, rubrics=rubrics)
    for event in events:
        retries = 0
        while retries < MAX_RETRIES:
            querystring = {"event_id": str(event.second_event_api_id), "locale": "en_INT"}
            response = requests.get(url, headers=HEADER_FOR_SECOND_API, params=querystring)
            if response.status_code == 200:
                response_data = response.json().get("DATA",[])
                first_element = response_data[0] if response_data else None
                if first_element:
                    video_link = first_element.get("PROPERTY_LINK")
                    video_id = video_link.split("=")[-1]
                    event.match_stream_link = video_id
                    event.save()
                break
            elif response.status_code == 429:
                retries += 1
                if retries < MAX_RETRIES:
                    if retries == MAX_RETRIES:
                        pass
                    time.sleep(1)
                    continue
                else:
                    pass
            else:
                pass
    return {"response": "get_match_stream_link successfully"}

@shared_task
def get_match_stream_links_id1():
    return get_match_stream_link(1)

@shared_task
def get_match_stream_links_id2():
    return get_match_stream_link(2)

@shared_task
def get_match_stream_links_id3():
    return get_match_stream_link(3)

@shared_task
def get_match_stream_links_id4():
    return get_match_stream_link(4)

@shared_task
def get_match_stream_links_id6():
    return get_match_stream_link(6)

@shared_task
def get_match_stream_links_id7():
    return get_match_stream_link(7)

@shared_task
def get_match_stream_links_id12():
    return get_match_stream_link(12)

@shared_task
def get_match_stream_links_id13():
    return get_match_stream_link(13)

@shared_task
def get_match_stream_links_id15():
    return get_match_stream_link(15)

@shared_task
def get_match_stream_links_id21():
    return get_match_stream_link(21)

@shared_task
def get_match_stream_links_id25():
    return get_match_stream_link(25)

@shared_task
def get_match_stream_links_id36():
    return get_match_stream_link(36)



def create_additional_info_for_events(rubric_id):
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    rubric = Rubrics.objects.get(api_id=rubric_id)
    events_h2h = Events.objects.filter(
        ~Q(status=2),
        h2h_status=False,
        rubrics=rubric,
        second_event_api_id__isnull=False,
        start_at__startswith=today_str
    )
    for event in events_h2h:
        response = requests.get(
            url="https://flashlive-sports.p.rapidapi.com/v1/events/h2h",
            headers=HEADER_FOR_SECOND_API,
            params={
                "locale": "en_INT",
                "event_id": event.second_event_api_id
            }
        )
        if response.status_code != 200:
            pass

        second_response_data = response.json().get("DATA", [])
        for el in second_response_data:
            groups = el.get("GROUPS")
            for group in groups:
                items = group.get("ITEMS", [])
                for item in items:
                    hi = item.get("HOME_IMAGES")
                    ai = item.get("AWAY_IMAGES")
                    logo_away, logo_home = item.get("AWAY_IMAGES"), item.get("HOME_IMAGES")
                    if logo_away:
                        logo_away = logo_away[-1]
                        logo_away = logo_away.replace('www.', 'static.')
                    else:
                        logo_away = ''
                    if logo_home:
                        logo_home = logo_home[-1]
                        logo_home = logo_home.replace('www.', 'static.')
                    else:
                        logo_home = ''
                    if hi is not None and ai is not None:
                        h2h, created = H2H.objects.get_or_create(
                            home_score=item.get("HOME_SCORE_FULL"),
                            away_score=item.get("AWAY_SCORE_FULL"),
                            name=item.get("EVENT_NAME"),
                            home_team_NAME=item.get("HOME_PARTICIPANT"),
                            home_team_LOGO=logo_home,
                            away_team_NAME=item.get("AWAY_PARTICIPANT"),
                            away_team_LOGO=logo_away,
                            league=item.get("EVENT_NAME"),
                            start_at=datetime.utcfromtimestamp(item.get("START_TIME")),
                            h_result=item.get("H_RESULT"),
                            team_mark=item.get("TEAM_MARK"),
                        )
                        event.h2h.add(h2h)
                        event.save()
            event.h2h_status = True
            event.save()
    events = Events.objects.filter(~Q(status=2),rubrics=rubric,player_status = False,start_at__startswith=today_str)
    for event in events:
        response = requests.get(
            url="https://flashlive-sports.p.rapidapi.com/v1/events/lineups",
            headers=HEADER_FOR_SECOND_API,
            params={
                "locale": "ru_RU",
                "event_id": event.second_event_api_id
            }
        )
        if response.status_code == 200:
            response_data = response.json().get("DATA")
            for data in response_data:
                formation_name = data.get("FORMATION_NAME")
                formations = data.get("FORMATIONS", [])
                for formation in formations:
                    team_line = formation.get("FORMATION_LINE")
                    if formation_name == 'Starting Lineups':
                        status_team_line = False
                    elif formation_name == 'Substitutes':
                        status_team_line = True
                    else :
                        status_team_line = False
                    members = formation.get("MEMBERS", [])
                    for player in members:
                        player_id = player.get("PLAYER_ID")
                        if player_id:
                            fields = {
                                "slug": f'{player_id}',
                                "name": player["PLAYER_FULL_NAME"],
                                "position_name": player.get("PLAYER_POSITION"),
                                "main_player": status_team_line,
                                "number": player.get("PLAYER_NUMBER"),
                                "photo": f'https://static.flashscore.com/res/image/data/{player.get("LPI")})'
                            }
                            player, created = Player.objects.get_or_create(
                                player_id=player_id,
                                # defaults={
                                #     "slug": f'{player["PLAYER_FULL_NAME"]} + {player["PLAYER_ID"]}',
                                #     "name": player["PLAYER_FULL_NAME"],
                                #     "position_name": player["PLAYER_POSITION"],
                                #     "description": player,
                                #     "main_player": True,
                                #     "number": player["PLAYER_NUMBER"],
                                # }
                            )
                            for field, value in fields.items():
                                if value:
                                    setattr(player, field, value)
                            if not formation_name == 'Starting Lineups':
                                setattr(player, "main_player", False)
                            player.save()
                            if team_line == 1:
                                event.home_team.players.add(player)
                            elif team_line == 2:
                                event.away_team.players.add(player)
    return {"response": "create_additional_info_for_events successfully"}


@shared_task
def create_additional_info_for_events_id1():
    return create_additional_info_for_events(1)



@shared_task
def create_additional_info_for_events_id2():
    return create_additional_info_for_events(2)


@shared_task
def create_additional_info_for_events_id3():
    return create_additional_info_for_events(3)


@shared_task
def create_additional_info_for_events_id4():
    return create_additional_info_for_events(4)


@shared_task
def create_additional_info_for_events_id6():
    return create_additional_info_for_events(6)


@shared_task
def create_additional_info_for_events_id7():
    return create_additional_info_for_events(7)


@shared_task
def create_additional_info_for_events_id12():
    return create_additional_info_for_events(12)


@shared_task
def create_additional_info_for_events_id13():
    return create_additional_info_for_events(13)


@shared_task
def create_additional_info_for_events_id15():
    return create_additional_info_for_events(15)


@shared_task
def create_additional_info_for_events_id21():
    return create_additional_info_for_events(21)


@shared_task
def create_additional_info_for_events_id25():
    return create_additional_info_for_events(25)


@shared_task
def create_additional_info_for_events_id36():
    return create_additional_info_for_events(36)
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
