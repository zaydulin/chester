from datetime import datetime, timedelta
from itertools import groupby
from django.views import View
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, TemplateView
from .models import Events, Rubrics, Season, Team, Player, Country, TimePeriod
from mainapp.models import Baners, Messages, Bookmarks
from mainapp.views import CustomHtmxMixin
from .forms import MessageForm, EventSearchForm
from django.http import JsonResponse, HttpResponseRedirect , HttpResponse
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from django.template.loader import render_to_string

def clear_db(request):
    duplicate_ids = Events.objects.values('second_event_api_id').annotate(count=Count('second_event_api_id')).filter(
        count__gt=1)
    count=0
    # Оставляем один объект с каждым значением second_event_api_id
    for duplicate_id in duplicate_ids:
        # Получаем первый объект с заданным second_event_api_id
        keep_event = Events.objects.filter(second_event_api_id=duplicate_id['second_event_api_id']).first()
        # Получаем все объекты, кроме первого
        delete_events = Events.objects.filter(second_event_api_id=duplicate_id['second_event_api_id']).exclude(id=keep_event.id)
        # Удаляем все объекты, кроме первого
        delete_events.delete()
        count+= 1
    return HttpResponse(f'ok - count{count }')

def update_events_status(request):
    events_to_update = Events.objects.filter(status=1)
    count = 0
    for event in events_to_update:
        event.status = 2
        event.save()
        count += 1
    return HttpResponse(f'ok - count{count}')

class HomeView(CustomHtmxMixin, TemplateView):
    """Категории"""
    model = Rubrics
    template_name = "event-list.html"

    def get_object(self, queryset=None):
        # Получаем объект категории по id
        if queryset is None:
            queryset = self.get_queryset()
        try:
            obj = queryset.first()
        except Rubrics.DoesNotExist:
            raise Http404("Категория не найдена")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rubric = Rubrics.objects.first()
        context["rubrics"] = rubric
        sidebar_baners = Baners.objects.filter(type=1)
        context["sidebar_baners"] = sidebar_baners

        gorizont_baners_top = Baners.objects.filter(type=2)
        context["gorizont_baners_top"] = gorizont_baners_top

        gorizont_baners_footer = Baners.objects.filter(type=3)
        context["gorizont_baners_footer"] = gorizont_baners_footer

        sidebar_baners_right = Baners.objects.filter(type=4)
        context["sidebar_baners_right"] = sidebar_baners_right

        sidebar_baners_left = Baners.objects.filter(type=5)
        context["sidebar_baners_left"] = sidebar_baners_left
        try:
            events = Events.objects.filter(status=1, rubrics=rubric).order_by("section__league_name", "-start_at")
            events_count = events.count()
            # Pagination
            if events_count < 20:
                paginator = Paginator(events, events_count)
            else:
                paginator = Paginator(events, 20)
            page = self.request.GET.get("page")

            try:
                events_page = paginator.page(page)
            except PageNotAnInteger:
                events_page = paginator.page(1)
            except EmptyPage:
                events_page = paginator.page(paginator.num_pages)

            grouped_events = {}

            for league_name, events_in_league in groupby(events_page, key=lambda event: event.section):
                grouped_events[league_name] = list(events_in_league)
            context["events"] = grouped_events
            context["paginator"] = paginator
        except :
            events_page = None
        context['title'] = f'{rubric.name} | Прямой эфир'
        context['meta_content'] = f'{rubric.name} | Прямой эфир'

        context["page_obj"] = events_page  # Pass the paginated events to the template

        return context


class EventsNow(CustomHtmxMixin, TemplateView):
    """Категории"""
    model = Rubrics
    template_name = "event-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rubric = Rubrics.objects.get(slug=kwargs.get('slug'))
        context["rubrics"] = rubric
        sidebar_baners = Baners.objects.filter(type=1)
        context["sidebar_baners"] = sidebar_baners

        gorizont_baners_top = Baners.objects.filter(type=2)
        context["gorizont_baners_top"] = gorizont_baners_top

        gorizont_baners_footer = Baners.objects.filter(type=3)
        context["gorizont_baners_footer"] = gorizont_baners_footer

        sidebar_baners_right = Baners.objects.filter(type=4)
        context["sidebar_baners_right"] = sidebar_baners_right

        sidebar_baners_left = Baners.objects.filter(type=5)
        context["sidebar_baners_left"] = sidebar_baners_left
        try:
            events = Events.objects.filter(status=1, rubrics=rubric).order_by("section__league_name", "-start_at")

            # Pagination
            events_count = events.count()
            # Pagination
            if events_count < 20:
                paginator = Paginator(events, events_count)
            else :
                paginator = Paginator(events, 20)
            page = self.request.GET.get("page")
            try:
                events_page = paginator.page(page)
            except PageNotAnInteger:
                events_page = paginator.page(1)
            except EmptyPage:
                events_page = paginator.page(paginator.num_pages)
            except Exception as e:
                events_page = None
            grouped_events = {}

            user = self.request.user

            for league_name, events_in_league in groupby(events_page, key=lambda event: event.section):
                events_list = list(events_in_league)
                for event in events_list:
                    # Check if the event or event.section is in the user's bookmarks
                    event_content_type = ContentType.objects.get_for_model(event)
                    league_content_type = ContentType.objects.get_for_model(event.section) if event.section else None
                    if self.request.user.is_authenticated:
                        event_bookmarked = Bookmarks.objects.filter(
                            user=user, content_type=event_content_type, object_id=event.id
                        ).exists()
                        league_bookmarked = (
                            Bookmarks.objects.filter(
                                user=user, content_type=league_content_type, object_id=event.section.id
                            ).exists()
                            if event.section
                            else False
                        )

                        event.is_bookmarked = event_bookmarked
                        event.section.is_bookmarked = league_bookmarked if event.section else False

                grouped_events[league_name] = events_list
            context["events"] = grouped_events
            context["paginator"] = paginator
        except :
            events_page = None

        context['title'] = f'{rubric.name} | Прямой эфир'
        context['meta_content'] = f'{rubric.name} | Прямой эфир'


        context["page_obj"] = events_page  # Pass the paginated events to the template

        return context


class EventsEndView(CustomHtmxMixin, TemplateView):
    """Категории"""
    model = Rubrics
    template_name = "event-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rubric = Rubrics.objects.get(slug = kwargs.get('slug'))
        context["rubrics"] = rubric
        sidebar_baners = Baners.objects.filter(type=1)
        context["sidebar_baners"] = sidebar_baners

        gorizont_baners_top = Baners.objects.filter(type=2)
        context["gorizont_baners_top"] = gorizont_baners_top

        gorizont_baners_footer = Baners.objects.filter(type=3)
        context["gorizont_baners_footer"] = gorizont_baners_footer

        sidebar_baners_right = Baners.objects.filter(type=4)
        context["sidebar_baners_right"] = sidebar_baners_right

        sidebar_baners_left = Baners.objects.filter(type=5)
        context["sidebar_baners_left"] = sidebar_baners_left
        try:
            events = Events.objects.filter(status=2, rubrics=rubric).order_by("section__league_name", "-start_at")

            events_count = events.count()
            # Pagination
            if events_count < 20:
                paginator = Paginator(events, events_count)
            else:
                paginator = Paginator(events, 20)
            page = self.request.GET.get("page")

            try:
                events_page = paginator.page(page)
            except PageNotAnInteger:
                events_page = paginator.page(1)
            except EmptyPage:
                events_page = paginator.page(paginator.num_pages)
            grouped_events = {}

            user = self.request.user
            for league_name, events_in_league in groupby(events_page, key=lambda event: event.section):
                events_list = list(events_in_league)
                for event in events_list:
                    # Check if the event or event.section is in the user's bookmarks
                    event_content_type = ContentType.objects.get_for_model(event)
                    league_content_type = ContentType.objects.get_for_model(event.section) if event.section else None
                    if user.is_authenticated:
                        event_bookmarked = Bookmarks.objects.filter(
                            user=user, content_type=event_content_type, object_id=event.id
                        ).exists()
                        league_bookmarked = (
                            Bookmarks.objects.filter(
                                user=user, content_type=league_content_type, object_id=event.section.id
                            ).exists()
                            if event.section
                            else False
                        )

                        event.is_bookmarked = event_bookmarked
                        event.section.is_bookmarked = league_bookmarked if event.section else False

                grouped_events[league_name] = events_list
            context["events"] = grouped_events
            context["paginator"] = paginator

        except :
            events_page = None
        context['title'] = f'{rubric.name} | Завершенные'
        context['meta_content'] = f'{rubric.name} | Завершенные'


        context["page_obj"] = events_page
          # Pass the paginated events to the template

        return context


class EventsUpcomingView(CustomHtmxMixin, TemplateView):
    """Категории"""
    model = Rubrics
    template_name = "event-list.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rubric_slug = self.kwargs['slug']

        rubric = Rubrics.objects.get(slug=rubric_slug)
        context['rubrics'] = rubric

        sidebar_baners = Baners.objects.filter(type=1)
        context["sidebar_baners"] = sidebar_baners

        gorizont_baners_top = Baners.objects.filter(type=2)
        context["gorizont_baners_top"] = gorizont_baners_top

        gorizont_baners_footer = Baners.objects.filter(type=3)
        context["gorizont_baners_footer"] = gorizont_baners_footer

        sidebar_baners_right = Baners.objects.filter(type=4)
        context["sidebar_baners_right"] = sidebar_baners_right

        sidebar_baners_left = Baners.objects.filter(type=5)
        context["sidebar_baners_left"] = sidebar_baners_left
        try:
            events = Events.objects.filter(status=3, rubrics=rubric).order_by("section__league_name", "-start_at")

            events_count = events.count()
            # Pagination
            if events_count < 20:
                paginator = Paginator(events, events_count)
            else:
                paginator = Paginator(events, 20)
            page = self.request.GET.get("page")

            try:
                events_page = paginator.page(page)
            except PageNotAnInteger:
                events_page = paginator.page(1)
            except EmptyPage:
                events_page = paginator.page(paginator.num_pages)

            grouped_events = {}

            user = self.request.user

            for league_name, events_in_league in groupby(events_page, key=lambda event: event.section):
                events_list = list(events_in_league)
                for event in events_list:
                    # Check if the event or event.section is in the user's bookmarks
                    event_content_type = ContentType.objects.get_for_model(event)
                    league_content_type = ContentType.objects.get_for_model(event.section) if event.section else None
                    if user.is_authenticated:
                        event_bookmarked = Bookmarks.objects.filter(
                            user=user, content_type=event_content_type, object_id=event.id
                        ).exists()
                        league_bookmarked = (
                            Bookmarks.objects.filter(
                                user=user, content_type=league_content_type, object_id=event.section.id
                            ).exists()
                            if event.section
                            else False
                        )

                        event.is_bookmarked = event_bookmarked
                        event.section.is_bookmarked = league_bookmarked if event.section else False

                grouped_events[league_name] = events_list
            context["events"] = grouped_events
            context["paginator"] = paginator
        except :
            events_page = None
        context['title'] = f'{rubric.name} | Предстоящие'
        context['meta_content'] = f'{rubric.name} | Предстоящие'

        context["page_obj"] = events_page  # Pass the paginated events to the template

        return context


class PostMessageView(View):
    def post(self, request, *args, **kwargs):
        event_slug = kwargs["event_slug"]
        event = Events.objects.filter(slug=event_slug).first()

        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        message_form = MessageForm(request.POST)

        if message_form.is_valid():
            message_text = message_form.cleaned_data["message"]
            message = Messages(user=user, message=message_text, event=event)
            message.save()

            messages = Messages.objects.filter(event=event)
            html_content = render_to_string("partials/chat_messages_form.html", {"messages": messages}).strip()

            # Возвращает JSON с HTML-кодом чата и информацией об успешном сохранении сообщения
            return JsonResponse({"success": True, "html": html_content, "message": "Сообщение успешно отправлено"})

        # Возвращает JSON с информацией об ошибке валидации формы
        return JsonResponse({"success": False, "errors": message_form.errors})

@require_GET
def get_chat_data(request, event_slug):
    event = Events.objects.filter(slug=event_slug).first()
    messages = Messages.objects.filter(event=event).order_by('-id')[:50]

    html_content = render_to_string("partials/chat_messages.html", {"messages": messages}).strip()

    return HttpResponse(html_content)



class EventsView(CustomHtmxMixin,TemplateView):
    model = Events
    template_name = "event-detail.html"
    slug_field = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_slug = kwargs["slug"]
        event = Events.objects.filter(slug=event_slug).first()
        home_team = event.home_team
        away_team = event.away_team
        no_comands = event.rubrics.sortable not in [
            1,
        ]
        context["no_comands"] = no_comands
        football = event.rubrics.sortable in [
            1,
        ]
        context["football"] = football
        hockey = event.rubrics.sortable in [
            2,
        ]
        context["hockey"] = hockey
        tennis = event.rubrics.sortable in [
            3,
        ]
        context["tennis"] = tennis
        messages = Messages.objects.filter(event=event).order_by('-id')
        page = self.request.GET.get('page', 1)
        paginator = Paginator(messages, 50)
        try:
            messages_page = paginator.page(page)
        except PageNotAnInteger:
            messages_page = paginator.page(1)
        except EmptyPage:
            messages_page = paginator.page(paginator.num_pages)

        message_form = MessageForm()
        unique_users_count = Messages.objects.filter(event=event).values("user").distinct().count()
        if home_team:
            home_team_players_main = home_team.players.filter(main_player=False)
            home_team_players_not_main = home_team.players.filter(main_player=True)
        else:
            home_team_players_main = []
            home_team_players_not_main = []
        if away_team:
            away_team_players_main = away_team.players.filter(main_player=False)
            away_team_players_not_main = away_team.players.filter(main_player=True)
        else:
            away_team_players_main = []
            away_team_players_not_main = []
        if self.request.user.is_authenticated:
            user = self.request.user
            season_bookmark = Bookmarks.objects.filter(
                user=user, content_type=ContentType.objects.get_for_model(Events), object_id=event.id
            ).first()
            context["is_event_bookmarked"] = season_bookmark is not None
            home_team_bookmark = Bookmarks.objects.filter(
                user=user, content_type=ContentType.objects.get_for_model(Team), object_id=home_team.id
            ).first()
            away_team_bookmark = Bookmarks.objects.filter(
                user=user, content_type=ContentType.objects.get_for_model(Team), object_id=away_team.id
            ).first()
            context["is_home_team_bookmarked"] = home_team_bookmark is not None
            context["is_away_team_bookmarked"] = away_team_bookmark is not None
        timeperiod = TimePeriod.objects.filter(event=event)
        context["title"] = f' {home_team.name} - {away_team.name}: смотреть онлайн {event.start_at} , прямая трансляция  бесплатно | Chesterbets'
        context["meta_content"] = f'{home_team.name} - {away_team.name} , ({event.rubrics.name}) , {event.start_at}. Онлайн видео трансляция, новости, статистика, ставки, прямой эфир.'
        context["event"] = event
        context["timeperiod"] = timeperiod
        context["messages_page"] = messages_page
        context["messages"] = messages
        context["message_form"] = message_form
        context["unique_users_count"] = unique_users_count
        context["home_team"] = home_team
        context["away_team"] = away_team
        context["eventslug"] = event.rubrics.slug
        context["home_team_players_main"] = home_team_players_main
        context["home_team_players_not_main"] = home_team_players_not_main
        context["away_team_players_main"] = away_team_players_main
        context["away_team_players_not_main"] = away_team_players_not_main
        return context

    def post(self, request, *args, **kwargs):
        event_slug = kwargs["slug"]
        event = Events.objects.get(slug=event_slug)
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            message_text = message_form.cleaned_data["message"]
            message = Messages(user=user, message=message_text, event=event)
            message.save()
        messages = Messages.objects.filter(event=event).order_by('-id')[:50]
        context["messages_page"] = messages
        return redirect("events_detail", slug=event_slug)

    def get_data(self, **kwargs):
        event_slug = kwargs["slug"]
        event = Events.objects.get(slug=event_slug)
        data = {
            "home_score": event.home_score,
            "away_score": event.home_score,
        }

        return JsonResponse(data)




class GetCurrentTimerView(View):
    def get(self, request, event_id):
        event = Events.objects.filter(id=event_id).first()
        data = {}
        template_name = 'partials/timer_div.html'
        if event:
            if event.half == 'HALF_TIME':
                data['timer_div'] = event.timer_div
                return render(request, template_name, data)
            else:
                pass
        else:
            return JsonResponse({'error': 'Event not found'}, status=404)

class GetElementDataView(View):
    def get(self, request, event_id, element):
        event = Events.objects.filter(id=event_id).first()
        data = {}
        if element == 'home_score':
            data['value'] = event.home_score
            data['idspan'] = 'score-home-head'
            template_name = 'partials/home_score.html'
        elif element == 'away_score':
            data['value'] = event.away_score
            data['idspan'] = 'score-away-head'
            template_name = 'partials/away_score.html'
        elif element == 'home_score_mid':
            data['value'] = event.home_score
            data['idspan'] = 'score-home-mid'
            template_name = 'partials/home_score.html'
        elif element == 'away_score_mid':
            data['value'] = event.away_score
            data['idspan'] = 'score-away-mid'
            template_name = 'partials/away_score.html'
        elif element == 'home_score_bttm':
            data['value'] = event.home_score
            data['idspan'] = 'score-home-bttm'
            template_name = 'partials/home_score.html'
        elif element == 'away_score_bttm':
            data['value'] = event.away_score
            data['idspan'] = 'score-away-bttm'
            template_name = 'partials/away_score.html'
        elif element == 'start_at':
            data['value'] = event.start_at
            template_name = 'partials/start_at.html'
        else:
            return JsonResponse({'error': 'Invalid element'})

        return render(request, template_name, data)


class SearchView(CustomHtmxMixin, TemplateView):
    template_name = "search.html"

    def get(self, request, *args, **kwargs):
        user = request.user
        rubric = Rubrics.objects.first()
        teams_get = request.GET.get("teams")
        league_get = request.GET.get("leagues")
        players_get = request.GET.get("players")
        search_description = request.GET.get("search_description")

        if "slug" not in kwargs:
            redirect_url = reverse("searchsec", kwargs={"slug": rubric.slug})
            if search_description:
                redirect_url += f"?search_description={search_description}"
            return HttpResponseRedirect(redirect_url)
        return super().get(request, teams=teams_get, leagues=league_get, players=players_get,*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = EventSearchForm(self.request.GET)
        teams_get = self.request.GET.get("teams")
        league_get = self.request.GET.get("leagues")
        players_get = self.request.GET.get("players")
        search_description = self.request.GET.get("search_description")
        rubric = Rubrics.objects.get(slug=kwargs["slug"])
        print('teams_get-----------', teams_get)
        print('league_get-----------', league_get)
        print('players_get-----------', players_get)

        if form.is_valid():
            events = Events.objects.filter(name__icontains=search_description, rubrics=rubric)
            teams = Team.objects.filter(name__icontains=search_description, rubrics=rubric)
            players = Player.objects.filter(name__icontains=search_description, team__rubrics=rubric)
            leagues = Season.objects.filter(league_name__icontains=search_description, rubrics=rubric)
        else:
            events = Events.objects.all()[:5]
            teams = Team.objects.all()[:5]
            players = Player.objects.all()[:5]
            leagues = Season.objects.all()[:5]

        sidebar_baners = Baners.objects.filter(type=1)
        context["sidebar_baners"] = sidebar_baners

        sidebar_baners_right = Baners.objects.filter(type=4)
        context["sidebar_baners_right"] = sidebar_baners_right

        sidebar_baners_left = Baners.objects.filter(type=5)
        context["sidebar_baners_left"] = sidebar_baners_left
        paginator = Paginator(events, 20)
        page_number = self.request.GET.get("page")
        try:
            events = paginator.page(page_number)
        except PageNotAnInteger:
            events = paginator.page(1)
        except EmptyPage:
            events = paginator.page(paginator.num_pages)

        paginator_teams = Paginator(teams, 20)
        paginator_leagues = Paginator(leagues, 20)
        paginator_players = Paginator(players, 20)

        page_number_teams = self.request.GET.get("teams_page")
        page_number_leagues = self.request.GET.get("leagues_page")
        page_number_players = self.request.GET.get("players_page")

        try:
            teams = paginator_teams.page(page_number_teams)
        except PageNotAnInteger:
            teams = paginator_teams.page(1)
        except EmptyPage:
            teams = paginator_teams.page(paginator_teams.num_pages)

        try:
            leagues = paginator_leagues.page(page_number_leagues)
        except PageNotAnInteger:
            leagues = paginator_leagues.page(1)
        except EmptyPage:
            leagues = paginator_leagues.page(paginator_leagues.num_pages)

        try:
            players = paginator_players.page(page_number_players)
        except PageNotAnInteger:
            players = paginator_players.page(1)
        except EmptyPage:
            players = paginator_players.page(paginator_players.num_pages)

        context["form"] = form
        if not teams_get and not league_get and not players_get:
            context["events"] = events
        if teams_get:
            context["teams"] = teams
        if league_get:
            context["leagues"] = leagues
        if players_get:
            context["players"] = players

        context["form"] = form

        # Добавим отладочную информацию
        context["rubrics"] = Rubrics.objects.all()
        context["rubriccontext"] = rubric.slug
        context["search_slug"] = kwargs.get("slug")
        context["search_description"] = search_description

        return context


class SeasonView(CustomHtmxMixin, TemplateView):
    model = Season
    template_name = "season-detail.html"
    slug_field = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_slug = kwargs["slug"]
        season = Season.objects.get(slug=event_slug)
        events = Events.objects.filter(section=season)
        sidebar_baners = Baners.objects.filter(type=1)
        context["sidebar_baners"] = sidebar_baners

        sidebar_baners_right = Baners.objects.filter(type=4)
        context["sidebar_baners_right"] = sidebar_baners_right

        sidebar_baners_left = Baners.objects.filter(type=5)
        context["sidebar_baners_left"] = sidebar_baners_left
        # Pagination
        paginator = Paginator(events, 20)  # 20 events per page
        page = self.request.GET.get("page")

        try:
            events_page = paginator.page(page)
        except PageNotAnInteger:
            events_page = paginator.page(1)
        except EmptyPage:
            events_page = paginator.page(paginator.num_pages)

        grouped_events = {}

        user = self.request.user

        for league_name, events_in_league in groupby(events_page, key=lambda event: event.section):
            events_list = list(events_in_league)
            if user.is_authenticated:
                for event in events_list:
                    event_content_type = ContentType.objects.get_for_model(event)

                    event_bookmarked = Bookmarks.objects.filter(
                        user=user, content_type=event_content_type, object_id=event.id
                    ).exists()

                    event.is_bookmarked = event_bookmarked

            grouped_events[league_name] = events_list

        context["events"] = grouped_events
        context["events_page"] = events_page

        context["season"] = season

        if self.request.user.is_authenticated:
            user = self.request.user
            season_bookmark = Bookmarks.objects.filter(
                user=user, content_type=ContentType.objects.get_for_model(Season), object_id=season.id
            ).first()
            context["is_season_bookmarked"] = season_bookmark is not None

        return context


class TeamView(CustomHtmxMixin, TemplateView):
    model = Team
    template_name = "team-detail.html"
    slug_field = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_slug = kwargs["slug"]
        team = Team.objects.get(slug=team_slug)
        event = Events.objects.filter(Q(home_team=team) | Q(away_team=team))
        # Pagination
        paginator = Paginator(event, 20)  # 20 events per page
        page = self.request.GET.get("page")
        sidebar_baners = Baners.objects.filter(type=1)
        context["sidebar_baners"] = sidebar_baners

        sidebar_baners_right = Baners.objects.filter(type=4)
        context["sidebar_baners_right"] = sidebar_baners_right

        sidebar_baners_left = Baners.objects.filter(type=5)
        context["sidebar_baners_left"] = sidebar_baners_left
        try:
            events_page = paginator.page(page)
        except PageNotAnInteger:
            events_page = paginator.page(1)
        except EmptyPage:
            events_page = paginator.page(paginator.num_pages)

        grouped_events = {}

        user = self.request.user

        for league_name, events_in_league in groupby(events_page, key=lambda event: event.section):
            events_list = list(events_in_league)
            for event in events_list:
                event_content_type = ContentType.objects.get_for_model(event)
                if user.is_authenticated:
                    event_bookmarked = Bookmarks.objects.filter(
                        user=user, content_type=event_content_type, object_id=event.id
                    ).exists()

                    event.is_bookmarked = event_bookmarked

            grouped_events[league_name] = events_list

        context["events"] = grouped_events
        context["team"] = team
        context["events_page"] = events_page

        if self.request.user.is_authenticated:
            user = self.request.user
            season_bookmark = Bookmarks.objects.filter(
                user=user, content_type=ContentType.objects.get_for_model(Team), object_id=team.id
            ).first()
            context["is_season_bookmarked"] = season_bookmark is not None
        return context


class PlayerView(CustomHtmxMixin, TemplateView):
    model = Player
    template_name = "player-detail.html"
    slug_field = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player_slug = kwargs["slug"]
        player = Player.objects.filter(slug=player_slug).first()
        team = Team.objects.filter(Q(players=player)).first()
        event = Events.objects.filter(Q(home_team=team) | Q(away_team=team))
        # Pagination
        paginator = Paginator(event, 20)  # 20 events per page
        page = self.request.GET.get("page")
        sidebar_baners = Baners.objects.filter(type=1)
        context["sidebar_baners"] = sidebar_baners

        sidebar_baners_right = Baners.objects.filter(type=4)
        context["sidebar_baners_right"] = sidebar_baners_right

        sidebar_baners_left = Baners.objects.filter(type=5)
        context["sidebar_baners_left"] = sidebar_baners_left
        try:
            events_page = paginator.page(page)
        except PageNotAnInteger:
            events_page = paginator.page(1)
        except EmptyPage:
            events_page = paginator.page(paginator.num_pages)

        grouped_events = {}

        user = self.request.user

        for league_name, events_in_league in groupby(events_page, key=lambda event: event.section):
            events_list = list(events_in_league)
            for event in events_list:
                # Check if the event or event.section is in the user's bookmarks
                event_content_type = ContentType.objects.get_for_model(event)
                league_content_type = ContentType.objects.get_for_model(event.section) if event.section else None
                if user.is_authenticated:
                    event_bookmarked = Bookmarks.objects.filter(
                        user=user, content_type=event_content_type, object_id=event.id
                    ).exists()
                    league_bookmarked = (
                        Bookmarks.objects.filter(
                            user=user, content_type=league_content_type, object_id=event.section.id
                        ).exists()
                        if event.section
                        else False
                    )
                    event.is_bookmarked = event_bookmarked
                    event.section.is_bookmarked = league_bookmarked if event.section else False
            grouped_events[league_name] = events_list
        context["events"] = grouped_events
        context["team"] = team
        context["player"] = player
        context["events_page"] = events_page
        if self.request.user.is_authenticated:
            user = self.request.user
            season_bookmark = Bookmarks.objects.filter(
                user=user, content_type=ContentType.objects.get_for_model(Team), object_id=team.id
            ).first()
            context["team_is_season_bookmarked"] = season_bookmark is not None
            user = self.request.user
            season_bookmark = Bookmarks.objects.filter(
                user=user, content_type=ContentType.objects.get_for_model(Player), object_id=player.id
            ).first()
            context["player_is_bookmarked"] = season_bookmark is not None

        return context

def get_next_elements(request):
    offset = int(request.GET['offset'])
    rubrics= int(request.GET['rubrics'])
    status= int(request.GET['status'])
    rubrics = Rubrics.objects.get(id=rubrics)
    events = Events.objects.filter(rubrics = rubrics,status=status).order_by("section__league_name", "-start_at")[offset:offset+20]
    context={ 'events':events , 'offset': offset+10}
    return render(request,'event_list_elements.html',context)
