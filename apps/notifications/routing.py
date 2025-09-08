"""
WebSocket routing for real-time notifications.
"""
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
    path('ws/notifications/<str:user_id>/', consumers.UserNotificationConsumer.as_asgi()),
]
