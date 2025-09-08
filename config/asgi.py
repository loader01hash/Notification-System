"""
ASGI config for notification system project.

Enhanced ASGI configuration with async support and WebSocket capability.
Falls back gracefully if channels is not installed.
"""

import os
import django
from django.core.asgi import get_asgi_application

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Setup Django first
django.setup()

# Get the Django ASGI application
django_asgi_app = get_asgi_application()

# Try to setup WebSocket support with channels
try:
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack
    from channels.security.websocket import AllowedHostsOriginValidator
    
    # Try to import WebSocket routing
    try:
        from apps.notifications.routing import websocket_urlpatterns
    except ImportError:
        websocket_urlpatterns = []
    
    # Enhanced ASGI application with WebSocket support
    application = ProtocolTypeRouter({
        # HTTP requests handled by Django
        "http": django_asgi_app,
        
        # WebSocket connections with authentication and security
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            )
        ),
    })
    
except ImportError:
    # Fallback to standard Django ASGI if channels not installed
    application = django_asgi_app
