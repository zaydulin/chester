from django.urls import re_path 

from . import  consumers

websocket_urlpatterns = [
    re_path(r'/events/(?P<slug>[-\w]+)/$', consumers.ChatConsumer.as_asgi()),
]
##################
