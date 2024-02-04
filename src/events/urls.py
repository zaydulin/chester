from django.urls import path
from . import views
from .views import get_chat_data

urlpatterns = [
    path('search/', views.SearchView.as_view(), name='search'),
    path('search/<slug:slug>', views.SearchView.as_view(), name='searchsec'),
    path('', views.HomeView.as_view(), name='home'),
    path('<slug:slug>/', views.EventsNow.as_view(), name='rubric'),
    path('<slug:slug>/end/', views.EventsEndView.as_view(), name='events_end'),
    path('<slug:slug>/upcoming/', views.EventsUpcomingView.as_view(), name='events_upcoming'),
    path('events/<slug:slug>/', views.EventsView.as_view(), name='events_detail'),
    path('league/<slug:slug>/', views.SeasonView.as_view(), name='season_detail'),
    path('team/<slug:slug>/', views.TeamView.as_view(), name='team_detail'),
    path('player/<slug:slug>/', views.PlayerView.as_view(), name='player_detail'),
    path('db/clear_db/', views.clear_db, name='clear_db'),
    path('get_chat_data/<slug:event_slug>/', get_chat_data, name='get_chat_data'),
    path('post_message/<slug:event_slug>/', views.PostMessageView.as_view(), name='post_message'),
]