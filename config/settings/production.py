"""
Production settings for the notification system.
"""
from .base import *

# Production settings
DEBUG = False

# Security settings for production
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600

# Logging for production
LOGGING['handlers']['file']['class'] = 'logging.handlers.RotatingFileHandler'
LOGGING['handlers']['file']['maxBytes'] = 1024 * 1024 * 10  # 10MB
LOGGING['handlers']['file']['backupCount'] = 5

# Cache configuration for production
CACHES['default']['TIMEOUT'] = 3600  # 1 hour
CACHES['default']['OPTIONS']['CONNECTION_POOL_KWARGS']['max_connections'] = 100

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Remove browsable API renderer in production
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
]
