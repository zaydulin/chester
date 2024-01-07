from django.urls import path
from . import views

urlpatterns = [
    path('check_sport_list/', views.check_sport_list, name='check_sport_list'),
    path('add_sport_events_list/', views.add_sport_events_list, name='add_sport_events_list'),
    path('add_sport_events_list_second/', views.add_sport_events_list_second, name='add_sport_events_list_second'),
    path('add_sport_events_list_second_online_gou/', views.add_sport_events_list_second_online_gou, name='add_sport_events_list_second_online_gou'),
    path('fetch_event_data/', views.fetch_event_data, name='fetch_event_data'),
    path('fetch_event_data_for_second/', views.fetch_event_data_for_second, name='fetch_event_data_for_second'),
    path('delete_h2h/', views.delete_h2h, name='delete_h2h'),

]