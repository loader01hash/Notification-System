"""
Development settings for the notification system.
"""
from .base import *

# Override DEBUG for development
DEBUG = True

# Development-specific apps
INSTALLED_APPS += [
    # Temporarily disable debug toolbar due to conflicts
    # 'debug_toolbar',
    'django_extensions',
]

# Development-specific middleware
MIDDLEWARE += [
    # Temporarily disable debug toolbar middleware
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug toolbar configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
    '0.0.0.0',
]

# Debug toolbar settings
def show_toolbar(request):
    """Custom toolbar callback to exclude schema endpoints"""
    if request.path.startswith('/api/schema') or request.path.startswith('/api/docs'):
        return False
    return DEBUG and request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest'

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
    'SHOW_COLLAPSED': False,
    'INSERT_BEFORE': '</head>',
    'RENDER_PANELS': True,
}

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.history.HistoryPanel',
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

# Email backend for development - using real SMTP for testing
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Disable caching in development
CACHES['default']['TIMEOUT'] = 1

# Development-specific logging
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# CORS - allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Redis Configuration for Celery
REDIS_URL = 'redis://localhost:6379'

# Celery Redis broker configuration
CELERY_BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'

# Redis connection pool settings
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_POOL_LIMIT = 10

# Additional Celery settings for development
CELERY_TASK_ALWAYS_EAGER = False  # Set to True to run tasks synchronously
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
