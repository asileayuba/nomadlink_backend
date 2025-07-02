from django.urls import re_path
from .consumers import EmergencyConsumer

websocket_urlpatterns = [
    re_path(r'^ws/emergency/$', EmergencyConsumer.as_asgi()),
]
