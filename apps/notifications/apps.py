"""
Notifications application configuration.
"""
from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = 'Notifications'
    
    def ready(self):
        """Initialize the application."""
        # Register notification channels
        from .channels import register_channels
        register_channels()
