from django.urls import path
from .views import trigger_emergency, my_emergencies, resolve_emergency, websocket_test_view

urlpatterns = [
    path('trigger/', trigger_emergency, name='trigger-emergency'),
    path('mine/', my_emergencies, name='my-emergencies'),
    path('resolve/<int:alert_id>/', resolve_emergency, name='resolve-emergency'),
    path('test-ws/', websocket_test_view, name='emergency-ws-test'),
]
