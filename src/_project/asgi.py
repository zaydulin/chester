# import os
# from django.core.asgi import get_asgi_application
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_project.settings")
# django_asgi_app = get_asgi_application()
#
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
#
# from events.routing import websocket_urlpatterns
#
# application = ProtocolTypeRouter(
#     {
#         "http": django_asgi_app,
#         "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
#     }
# )
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'megafarm.settings')

application = get_asgi_application()
