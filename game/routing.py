from django.urls import re_path
from . import consumers
from . arena import Player

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', Player.as_asgi()),
    re_path(r'ws/test_game/$', consumers.GameConsumer.as_asgi())
]


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
