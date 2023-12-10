from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('pages/<slug:slug>/', views.PageDetailView.as_view(), name='pages'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('registration/', views.RegistrationView.as_view(), name='register'),
    path('account/', views.EditProfileView.as_view(), name='edit_profile'),
    path('favorite/', views.FavoriteView.as_view(), name='favorite'),
    path('favorite/<str:bookmark_sort_by>/<slug:slug>', views.FavoriteView.as_view(), name='favoritesec'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('toggle_bookmark/<str:bookmark_type>/<int:item_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('toggle_bookmark_post/', views.toggle_bookmark_post, name='toggle_bookmark_post'),
    path('get_incidents_event_post/', views.get_incidents_event_post, name='get_incidents_event_post'),

]