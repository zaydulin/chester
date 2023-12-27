
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, UpdateView
from events.models import Events, Season, Team, Player, Rubrics
from .models import Pages, User, GeneralSettings, Baners, Bookmarks
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import LoginForm, UserProfileForm, RegistrationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
import time
from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse, HttpResponse
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta

class CustomHtmxMixin:
    def dispatch(self, request, *args, **kwargs):
        self.template_htmx = self.template_name
        if not self.request.META.get('HTTP_HX_REQUEST'):
            self.template_name = 'themes/include_block.html'
        else:
            time.sleep(1)
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        kwargs['template_htmx'] = self.template_htmx
        return super().get_context_data(**kwargs)

def toggle_bookmark(request, bookmark_type, item_id):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if bookmark_type == 'season':
        try:
            season = Season.objects.get(id=item_id)
        except Season.DoesNotExist:
            return HttpResponseRedirect(reverse('home'))
        content_type = ContentType.objects.get_for_model(season)
    elif bookmark_type == 'event':
        try:
            event = Events.objects.get(id=item_id)
        except Events.DoesNotExist:
            return HttpResponseRedirect(reverse('home'))
        content_type = ContentType.objects.get_for_model(event)
    elif bookmark_type == 'team':
        try:
            team = Team.objects.get(id=item_id)
        except Events.DoesNotExist:
            return HttpResponseRedirect(reverse('home'))
        content_type = ContentType.objects.get_for_model(team)
    elif bookmark_type == 'player':
        try:
            team = Player.objects.get(id=item_id)
        except Events.DoesNotExist:
            return HttpResponseRedirect(reverse('home'))
        content_type = ContentType.objects.get_for_model(team)
    else:
        return HttpResponseBadRequest('Invalid bookmark type')

    if Bookmarks.objects.filter(user=user, content_type=content_type, object_id=item_id).exists():
        Bookmarks.objects.filter(user=user, content_type=content_type, object_id=item_id).delete()
    else:
        Bookmarks.objects.create(user=user, content_type=content_type, object_id=item_id)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
def toggle_bookmark_post(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    bookmark_type = request.POST.get('bookmark_type')
    item_id = request.POST.get('event_id')
    if bookmark_type == 'event':
        try:
            event = Events.objects.get(id=item_id)
        except Events.DoesNotExist:
            return HttpResponseRedirect(reverse('home'))
        content_type = ContentType.objects.get_for_model(event)
    elif bookmark_type == 'team':
        try:
            team = Team.objects.get(id=item_id)
        except Team.DoesNotExist:
            return HttpResponseRedirect(reverse('home'))
        content_type = ContentType.objects.get_for_model(team)
    elif bookmark_type == 'season':
        try:
            season = Season.objects.get(id=item_id)
        except Season.DoesNotExist:
            return HttpResponseRedirect(reverse('home'))
        content_type = ContentType.objects.get_for_model(season)
    else:
        return HttpResponseBadRequest('Invalid bookmark type')

    if Bookmarks.objects.filter(user=user, content_type=content_type, object_id=item_id).exists():
        Bookmarks.objects.filter(user=user, content_type=content_type, object_id=item_id).delete()
    else:
        Bookmarks.objects.create(user=user, content_type=content_type, object_id=item_id)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def get_incidents_event_post(request):
    events = Rubrics.objects.filter(second_api=True)
    return HttpResponseBadRequest(f'{events}')


class EditProfileView(CustomHtmxMixin, TemplateView):
    template_name = 'profile.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = UserProfileForm(instance=request.user)
        context = self.get_context_data(form=form, title='Личные данные')
        return self.render_to_response(context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('edit_profile')
        context = self.get_context_data(form=form, title='Личные данные')
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        kwargs['title'] = 'Профиль'
        return super().get_context_data(**kwargs)


class PageDetailView(CustomHtmxMixin, DetailView):
    """Страницф"""
    model = Pages
    template_name = 'page.html'
    slug_field = "slug"
    context_object_name = 'pages'

    def get_context_data(self, **kwargs):
        page = self.get_object()
        kwargs['title'] = page.name
        kwargs['meta_description'] = page.content

        return super().get_context_data(**kwargs)

class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(
                'edit_profile')  # Если пользователь уже авторизован, перенаправьте его на страницу 'edit_profile'

        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.blocked:
                    messages.error(request, "Ваш аккаунт заблокирован.")
                    return redirect('login')
                login(request, user)
                return redirect('edit_profile')
        return render(request, self.template_name, {'form': form,'message':''})

class RegistrationView(View):
    template_name = 'register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('edit_profile')

        general_settings = GeneralSettings.objects.first()

        if general_settings.registration == 1:
            form = RegistrationForm()
            return render(request, self.template_name, {'form': form})
        else:
            return render(request, self.template_name, {'message': general_settings.of_register_message})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('edit_profile')

        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('edit_profile')
        return render(request, self.template_name, {'form': form})

class FavoriteView(CustomHtmxMixin, TemplateView):
    template_name = 'favorite.html'
    paginate_by = 2

    def get(self, request,*args, **kwargs):
        user = request.user
        rubric =Rubrics.objects.first()

        if not user.is_authenticated:
            return redirect('login')
        else:
            if 'bookmark_sort_by' and 'slug' not in kwargs:
                redirect_url = reverse('favoritesec', kwargs={'bookmark_sort_by': 'shedule' ,'slug': rubric.slug })
                return HttpResponseRedirect(redirect_url)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kwargs['title'] = 'Избранные'
        bookmark_sort_by = kwargs['bookmark_sort_by']
        slug = kwargs['slug']
        time = self.request.GET.get('time')
        rubric = Rubrics.objects.get(slug=slug)
        rubrics =  Rubrics.objects.all()
        sidebar_baners = Baners.objects.filter(type=1)
        context['sidebar_baners'] = sidebar_baners
        context['slugofpage'] = slug
        context['rubric'] = rubric
        context['rubrics'] = rubrics
        context['bookmark_sort_by'] = bookmark_sort_by

        sidebar_baners_right = Baners.objects.filter(type=4)
        context['sidebar_baners_right'] = sidebar_baners_right

        sidebar_baners_left = Baners.objects.filter(type=5)
        context['sidebar_baners_left'] = sidebar_baners_left

        bookmarks = Bookmarks.objects.filter(user = self.request.user)
        # Создайте списки для хранения объектов Event и Season из закладок
        event_bookmarks = []
        season_bookmarks = []
        team_bookmarks = []
        player_bookmarks = []
        event_bookmarks_day = []

        for bookmark in bookmarks:
            if bookmark.content_type.model == 'events':
                try:
                    event = get_object_or_404(Events, id=bookmark.object_id,rubrics=rubric)

                    event_bookmarks.append(event)
                except:pass

            elif bookmark.content_type.model == 'events':
                if time:
                    event = get_object_or_404(Events, id=bookmark.object_id, rubrics=rubric, start_at__date=time)
                    event_bookmarks_day.append(event)
            elif bookmark.content_type.model == 'season':
                try:
                    season = get_object_or_404(Season, id=bookmark.object_id,rubrics=rubric)
                    season_bookmarks.append(season)
                except:pass
            elif bookmark.content_type.model == 'team':
                try:
                    team = get_object_or_404(Team, id=bookmark.object_id,rubrics=rubric)
                    team_bookmarks.append(team)
                except:pass
            elif bookmark.content_type.model == 'player':
                try:
                    player = get_object_or_404(Player, id=bookmark.object_id,team__rubrics=rubric)
                    player_bookmarks.append(player)
                except: pass

        if bookmark_sort_by == 'shedule' :
            context['event_bookmarks'] = event_bookmarks
        elif bookmark_sort_by == 'players':
            context['player_bookmarks'] = player_bookmarks
        elif bookmark_sort_by == 'teams':
            context['team_bookmarks'] = team_bookmarks
        elif bookmark_sort_by == 'league':
            context['season_bookmarks'] = season_bookmarks
        elif bookmark_sort_by == 'for_time':
            if time:
                context['event_bookmarks_day'] = event_bookmarks_day
            else:pass
        today = datetime.now()
        context['today'] = today
        end_date = today + timedelta(days=6)
        day_list = []
        while today <= end_date:
            day_list.append(today)
            today += timedelta(days=1)

        context['day_list'] = day_list

        return context
