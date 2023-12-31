from django.urls import path
from . import views

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

]