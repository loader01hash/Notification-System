"""
Alternative development settings without debug toolbar to avoid the 'djdt' namespace issue.
Use this if you encounter debug toolbar problems.
"""
from .base import *

# Override DEBUG for development
DEBUG = True

# Development-specific apps (without debug_toolbar)
INSTALLED_APPS += [
    'django_extensions',
]

# Development-specific middleware (without debug_toolbar)
# MIDDLEWARE += []

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable caching in development
CACHES['default']['TIMEOUT'] = 1

# Development-specific logging
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# CORS - allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Alternative settings if debug toolbar causes issues
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,  # Disable toolbar
}
