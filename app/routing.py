from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'directos/ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'correccion/ws/(?P<user_id>\w+)/$', consumers.CorreccionConsumer.as_asgi()),
]