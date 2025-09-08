"""
Celery configuration for the notification system.
"""
import os
from celery import Celery
from decouple import config

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('notification_system')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Configuration
app.conf.update(
    broker_url=config('CELERY_BROKER_URL', default='redis://localhost:6379/1'),
    result_backend=config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/2'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
    # Add Redis connection pool settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_pool_limit=10,
    result_backend_transport_options={
        'master_name': None,
        'visibility_timeout': 3600,
        'retry_policy': {
            'timeout': 5.0
        }
    },
    task_routes={
        'apps.notifications.tasks.*': {'queue': 'default'},
        'apps.orders.tasks.*': {'queue': 'default'},
    },
)


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f'Request: {self.request!r}')
