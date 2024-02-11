import time
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (PasswordResetConfirmView,
                                       PasswordResetView)
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.http import (Http404, HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect, JsonResponse)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView, UpdateView

from events.models import Events, Player, Rubrics, Season, Team

from .forms import (LoginForm, RegistrationForm, SetEmailForm,
                    UserForgotPasswordForm, UserProfileForm,
                    UserSetNewPasswordForm)
from .models import Baners, Bookmarks, GeneralSettings, Pages, User

try:
    import _project.settings.core_settings as core_settings
except ImportError:
    import _project.settings.local_settings as core_settings


class CustomHtmxMixin:
    def dispatch(self, request, *args, **kwargs):
        self.template_htmx = self.template_name
        if not self.request.META.get("HTTP_HX_REQUEST"):
            self.template_name = "themes/include_block.html"
        else:
            time.sleep(1)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs["template_htmx"] = self.template_htmx
        return super().get_context_data(**kwargs)


def toggle_bookmark(request, bookmark_type, item_id):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if bookmark_type == "season":
        try:
            season = Season.objects.get(id=item_id)
        except Season.DoesNotExist:
            return HttpResponseRedirect(reverse("home"))
        content_type = ContentType.objects.get_for_model(season)
    elif bookmark_type == "event":
        try:
            event = Events.objects.get(id=item_id)
        except Events.DoesNotExist:
            return HttpResponseRedirect(reverse("home"))
        content_type = ContentType.objects.get_for_model(event)
    elif bookmark_type == "team":
        try:
            team = Team.objects.get(id=item_id)
        except Events.DoesNotExist:
            return HttpResponseRedirect(reverse("home"))
        content_type = ContentType.objects.get_for_model(team)
    elif bookmark_type == "player":
        try:
            team = Player.objects.get(id=item_id)
        except Events.DoesNotExist:
            return HttpResponseRedirect(reverse("home"))
        content_type = ContentType.objects.get_for_model(team)
    else:
        return HttpResponseBadRequest("Invalid bookmark type")

    if Bookmarks.objects.filter(user=user, content_type=content_type, object_id=item_id).exists():
        Bookmarks.objects.filter(user=user, content_type=content_type, object_id=item_id).delete()
    else:
        Bookmarks.objects.create(user=user, content_type=content_type, object_id=item_id)

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def toggle_bookmark_post(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    bookmark_type = request.POST.get("bookmark_type")
    item_id = request.POST.get("event_id")
    if bookmark_type == "event":
        try:
            event = Events.objects.get(id=item_id)
        except Events.DoesNotExist:
            return HttpResponseRedirect(reverse("home"))
        content_type = ContentType.objects.get_for_model(event)
    elif bookmark_type == "team":
        try:
            team = Team.objects.get(id=item_id)
        except Team.DoesNotExist:
            return HttpResponseRedirect(reverse("home"))
        content_type = ContentType.objects.get_for_model(team)
    elif bookmark_type == "season":
        try:
            season = Season.objects.get(id=item_id)
        except Season.DoesNotExist:
            return HttpResponseRedirect(reverse("home"))
        content_type = ContentType.objects.get_for_model(season)
    else:
        return HttpResponseBadRequest("Invalid bookmark type")

    if bookmark_object := Bookmarks.objects.filter(user=user, content_type=content_type, object_id=item_id):
        bookmark_object.delete()
    else:
        Bookmarks.objects.create(user=user, content_type=content_type, object_id=item_id)

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class EditProfileView(CustomHtmxMixin, TemplateView):
    template_name = "profile.html"

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = UserProfileForm(instance=request.user)
        emailform = SetEmailForm()  # Создаем экземпляр формы SetEmailForm
        context = self.get_context_data(form=form, emailform=emailform, title="Личные данные")
        return self.render_to_response(context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("edit_profile")
        context = self.get_context_data(form=form, title="Личные данные")
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        kwargs["title"] = "Профиль"
        return super().get_context_data(**kwargs)


class EmailExistsView(TemplateView):
    template_name = "profiles/email_is_exists.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Данный адрес уже занят."
        return context


class PageDetailView(CustomHtmxMixin, DetailView):
    """Страницф"""

    model = Pages
    template_name = "page.html"
    slug_field = "slug"
    context_object_name = "pages"

    def get_context_data(self, **kwargs):
        page = self.get_object()
        kwargs["title"] = page.name
        kwargs["meta_description"] = page.content

        return super().get_context_data(**kwargs)


class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(
                "edit_profile"
            )  # Если пользователь уже авторизован, перенаправьте его на страницу 'edit_profile'

        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            print("yes")
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.blocked:
                    messages.error(request, "Ваш аккаунт заблокирован.")
                    return redirect("login")
                login(request, user)
                return redirect("edit_profile")
            else:
                messages.error(request, "Пользователь не найден")
                return redirect("login")
        else:
            print("yes")
            messages.error(request, "Неверные данные формы")
        return render(request, self.template_name, {"form": form})


class RegistrationView(View):
    template_name = "register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("edit_profile")

        general_settings = GeneralSettings.objects.first()

        if general_settings.registration == 1:
            form = RegistrationForm()
            return render(request, self.template_name, {"form": form})
        else:
            return render(request, self.template_name, {"message": general_settings.of_register_message})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("edit_profile")

        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            token = default_token_generator.make_token(self.request.user)
            uid = urlsafe_base64_encode(force_bytes(self.request.user.pk))
            activation_url = reverse_lazy("confirm_email", kwargs={"uidb64": uid, "token": token})
            send_mail(
                "Подтвердите свой электронный адрес",
                f"Пожалуйста, перейдите по следующей ссылке, чтобы подтвердить свой адрес электронной почты: https://chesterbets.com{activation_url}",
                core_settings.EMAIL_HOST_USER,
                [self.request.user.email],
                fail_silently=False,
            )
            return redirect("confirm_sent")
        return render(request, self.template_name, {"form": form})


class UserConfirmChangeEmailView(View):
    def get(self, request, uidb64, token, email):
        if self.request.user.is_authenticated:
            try:
                uid = urlsafe_base64_decode(uidb64)
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                user.email = email
                user.save()
                return redirect("email_confirmed")
            else:
                return redirect("email_confirmation_failed")
        else:
            return redirect("login")


class EmailConfirmationSentView(TemplateView):
    template_name = "profiles/email_verification_sent.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            "title"
        ] = "На вашу почту была отправлена ссылка с подтверждением. Подтвердите почту, иначе регистарция не будет завершена"
        return context


class ChangeEmail(View):
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        user = self.request.user
        emailform = SetEmailForm(request.POST or None)
        if emailform.is_valid():
            email = emailform.cleaned_data["email"]
            if User.objects.filter(email=email):
                return redirect("email_is_exist")
            else:
                token = default_token_generator.make_token(self.request.user)
                uid = urlsafe_base64_encode(force_bytes(self.request.user.pk))
                activation_url = reverse_lazy(
                    "confirm_change_email", kwargs={"uidb64": uid, "token": token, "email": email}
                )
                send_mail(
                    "Подтвердите свой электронный адрес",
                    f"Пожалуйста, перейдите по следующей ссылке, чтобы подтвердить свой адрес электронной почты: https://chesterbets.com{activation_url}",
                    settings.EMAIL_HOST_USER,  # Access EMAIL_HOST_USER from settings
                    [email],
                    fail_silently=False,
                )
                return redirect("confirm_sent")


class UserConfirmEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect("email_confirmed")
        else:
            return redirect("email_confirmation_failed")


class EmailConfirmedView(TemplateView):
    template_name = "profiles/email_confirmed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Ваш электронный адрес активирован"
        return context


class EmailConfirmationFailedView(TemplateView):
    template_name = "profiles/email_confirm_failed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Ваш электронный адрес не активирован"
        return context


class PasswordResetSentView(TemplateView):
    template_name = "profiles/password_reset_sent.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "На вашу почту выслана инструкция по восстановлению пароля."
        return context


class UserForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    form_class = UserForgotPasswordForm
    template_name = "profiles/user_password_reset.html"
    success_url = reverse_lazy("reset_sent")
    subject_template_name = "profiles/password_subject_reset_mail.txt"
    email_template_name = "profiles/password_reset_mail.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated == True:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user_email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            messages.error(self.request, "Пользователь с указанным адресом электронной почты не существует.")
            return super().form_invalid(form)
        if user.is_active == False:
            messages.error(self.request, "Вы не подтвердили свой email, восстановление пароля невозможно.")
            return super().form_invalid(form)

        return super().form_valid(form)


class UserPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    form_class = UserSetNewPasswordForm
    template_name = "profiles/user_password_set_new.html"
    success_url = reverse_lazy("home")
    success_message = "Пароль успешно изменен. Можете авторизоваться на сайте."

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated == True:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)


class FavoriteView(CustomHtmxMixin, TemplateView):
    template_name = "favorite.html"
    paginate_by = 2

    def get(self, request, *args, **kwargs):
        user = request.user
        rubric = Rubrics.objects.first()

        if not user.is_authenticated:
            return redirect("login")
        else:
            if "bookmark_sort_by" and "slug" not in kwargs:
                redirect_url = reverse("favoritesec", kwargs={"bookmark_sort_by": "shedule", "slug": rubric.slug})
                return HttpResponseRedirect(redirect_url)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kwargs["title"] = "Избранные"
        bookmark_sort_by = kwargs["bookmark_sort_by"]
        slug = kwargs["slug"]
        time = self.request.GET.get("time")
        rubric = Rubrics.objects.get(slug=slug)
        rubrics = Rubrics.objects.all()
        sidebar_baners = Baners.objects.filter(type=1)
        context["sidebar_baners"] = sidebar_baners
        context["slugofpage"] = slug
        context["rubric"] = rubric
        context["rubrics"] = rubrics
        context["bookmark_sort_by"] = bookmark_sort_by

        sidebar_baners_right = Baners.objects.filter(type=4)
        context["sidebar_baners_right"] = sidebar_baners_right

        sidebar_baners_left = Baners.objects.filter(type=5)
        context["sidebar_baners_left"] = sidebar_baners_left

        bookmarks = Bookmarks.objects.filter(user=self.request.user)
        # Создайте списки для хранения объектов Event и Season из закладок
        event_bookmarks = []
        season_bookmarks = []
        team_bookmarks = []
        player_bookmarks = []
        event_bookmarks_day = []

        for bookmark in bookmarks:
            if bookmark.content_type.model == "events":
                try:
                    event = get_object_or_404(Events, id=bookmark.object_id, rubrics=rubric)

                    event_bookmarks.append(event)
                except:
                    pass

            elif bookmark.content_type.model == "events":
                if time:
                    event = get_object_or_404(Events, id=bookmark.object_id, rubrics=rubric, start_at__date=time)
                    event_bookmarks_day.append(event)
            elif bookmark.content_type.model == "season":
                try:
                    season = get_object_or_404(Season, id=bookmark.object_id, rubrics=rubric)
                    season_bookmarks.append(season)
                except:
                    pass
            elif bookmark.content_type.model == "team":
                try:
                    team = get_object_or_404(Team, id=bookmark.object_id, rubrics=rubric)
                    team_bookmarks.append(team)
                except:
                    pass
            elif bookmark.content_type.model == "player":
                try:
                    player = get_object_or_404(Player, id=bookmark.object_id, team__rubrics=rubric)
                    player_bookmarks.append(player)
                except:
                    pass

        if bookmark_sort_by == "shedule":
            context["event_bookmarks"] = event_bookmarks
        elif bookmark_sort_by == "players":
            context["player_bookmarks"] = player_bookmarks
        elif bookmark_sort_by == "teams":
            context["team_bookmarks"] = team_bookmarks
        elif bookmark_sort_by == "league":
            context["season_bookmarks"] = season_bookmarks
        elif bookmark_sort_by == "for_time":
            if time:
                context["event_bookmarks_day"] = event_bookmarks_day
            else:
                pass
        today = datetime.now()
        context["today"] = today
        end_date = today + timedelta(days=6)
        day_list = []
        while today <= end_date:
            day_list.append(today)
            today += timedelta(days=1)

        context["day_list"] = day_list

        return context
