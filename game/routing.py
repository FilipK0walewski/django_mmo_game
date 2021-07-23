from django.urls import re_path
from . import consumers

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

websocket_urlpatterns = [
    re_path(r'ws/test_game/$', consumers.GameConsumer.as_asgi())
]

# channel_routing = {}

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
