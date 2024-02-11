from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("pages/<slug:slug>/", views.PageDetailView.as_view(), name="pages"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("registration/", views.RegistrationView.as_view(), name="register"),
    path("account/", views.EditProfileView.as_view(), name="edit_profile"),
    path("favorite/", views.FavoriteView.as_view(), name="favorite"),
    path("favorite/<str:bookmark_sort_by>/<slug:slug>", views.FavoriteView.as_view(), name="favoritesec"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("toggle_bookmark/<str:bookmark_type>/<int:item_id>/", views.toggle_bookmark, name="toggle_bookmark"),
    path("toggle_bookmark_post/", views.toggle_bookmark_post, name="toggle_bookmark_post"),
    path("password-reset/", views.UserForgotPasswordView.as_view(), name="password_reset"),
    path(
        "set-new-password/<uidb64>/<token>/",
        views.UserPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("confirm-email/<str:uidb64>/<str:token>/", views.UserConfirmEmailView.as_view(), name="confirm_email"),
    path(
        "confirm-change-email/<str:uidb64>/<str:token>/<str:email>/",
        views.UserConfirmChangeEmailView.as_view(),
        name="confirm_change_email",
    ),
    path("confirm_sent/", views.EmailConfirmationSentView.as_view(), name="confirm_sent"),
    path("password-reset-sent/", views.PasswordResetSentView.as_view(), name="reset_sent"),
    path("email-confirmed/", views.EmailConfirmedView.as_view(), name="email_confirmed"),
    path("confirm-email-failed/", views.EmailConfirmationFailedView.as_view(), name="email_confirmation_failed"),
    path("changeemail/", views.ChangeEmail.as_view(), name="changeemail"),
    path("emailisexist/", views.EmailExistsView.as_view(), name="email_is_exist"),
]
