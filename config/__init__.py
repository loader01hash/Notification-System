"""
Configuration package for the notification system.
"""

# Import the Celery app so it can be discovered
from .celery import app as celery_app

__all__ = ('celery_app',)
