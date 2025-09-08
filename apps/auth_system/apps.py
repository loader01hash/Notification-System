"""
Authentication system app configuration.
"""
from django.apps import AppConfig


class AuthSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auth_system'
    verbose_name = 'Authentication System'
