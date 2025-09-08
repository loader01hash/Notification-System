"""
API Gateway views for system monitoring and health checks.
"""
import time
import psutil
from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
import redis
import logging

from .serializers import (
    HealthCheckSerializer,
    MetricsSerializer,
    SystemStatusSerializer
)

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """Health check endpoint for load balancer."""
    
    permission_classes = [AllowAny]
    serializer_class = HealthCheckSerializer
    
    @extend_schema(
        responses=HealthCheckSerializer,
        description="Health check endpoint for load balancer monitoring"
    )
    def get(self, request):
        """Return health status of the application."""
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'checks': {}
        }
        
        # Check database connection
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status['checks']['database'] = 'healthy'
        except Exception as e:
            health_status['checks']['database'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        # Check Redis connection
        try:
            cache.get('health_check')
            health_status['checks']['redis'] = 'healthy'
        except Exception as e:
            health_status['checks']['redis'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        # Check Celery workers
        try:
            from celery import current_app
            inspect = current_app.control.inspect()
            active_workers = inspect.active()
            if active_workers:
                health_status['checks']['celery'] = 'healthy'
            else:
                health_status['checks']['celery'] = 'no_workers'
                health_status['status'] = 'degraded'
        except Exception as e:
            health_status['checks']['celery'] = f'unhealthy: {str(e)}'
            health_status['status'] = 'unhealthy'
        
        response_status = status.HTTP_200_OK
        if health_status['status'] == 'unhealthy':
            response_status = status.HTTP_503_SERVICE_UNAVAILABLE
        elif health_status['status'] == 'degraded':
            response_status = status.HTTP_200_OK
        
        return Response(health_status, status=response_status)


class MetricsView(APIView):
    """Metrics endpoint for monitoring."""
    
    permission_classes = [AllowAny]
    serializer_class = MetricsSerializer
    
    @extend_schema(
        responses=MetricsSerializer,
        description="System and application metrics for monitoring"
    )
    def get(self, request):
        """Return application metrics."""
        metrics = {
            'timestamp': time.time(),
            'system': self._get_system_metrics(),
            'application': self._get_application_metrics(),
        }
        
        return Response(metrics)
    
    def _get_system_metrics(self):
        """Get system-level metrics."""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else None,
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {'error': str(e)}
    
    def _get_application_metrics(self):
        """Get application-level metrics."""
        try:
            # Get cache statistics
            cache_stats = {}
            try:
                redis_client = redis.from_url(settings.CACHES['default']['LOCATION'])
                info = redis_client.info()
                cache_stats = {
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory': info.get('used_memory', 0),
                    'hits': info.get('keyspace_hits', 0),
                    'misses': info.get('keyspace_misses', 0),
                }
            except Exception:
                cache_stats = {'error': 'Unable to get cache stats'}
            
            return {
                'cache': cache_stats,
                'database_connections': self._get_db_connections(),
            }
        except Exception as e:
            logger.error(f"Error getting application metrics: {e}")
            return {'error': str(e)}
    
    def _get_db_connections(self):
        """Get database connection count."""
        try:
            from django.db import connection
            return {
                'active_connections': len(connection.queries) if settings.DEBUG else 'N/A'
            }
        except Exception:
            return {'error': 'Unable to get DB connection count'}


class SystemStatusView(APIView):
    """System status endpoint for detailed monitoring."""
    
    permission_classes = [AllowAny]
    serializer_class = SystemStatusSerializer
    
    @extend_schema(
        responses=SystemStatusSerializer,
        description="Detailed system status including services and configuration"
    )
    def get(self, request):
        """Return detailed system status."""
        status_info = {
            'timestamp': time.time(),
            'version': getattr(settings, 'VERSION', '1.0.0'),
            'environment': 'development' if settings.DEBUG else 'production',
            'services': self._check_services(),
            'configuration': self._get_configuration_status(),
        }
        
        return Response(status_info)
    
    def _check_services(self):
        """Check status of dependent services."""
        services = {}
        
        # Check notification channels
        services['notification_channels'] = self._check_notification_channels()
        
        # Check external services
        services['external'] = self._check_external_services()
        
        return services
    
    def _check_notification_channels(self):
        """Check notification channel availability."""
        channels = {}
        
        # Check Telegram
        telegram_config = settings.NOTIFICATION_CONFIG.get('TELEGRAM', {})
        if telegram_config.get('BOT_TOKEN'):
            channels['telegram'] = 'configured'
        else:
            channels['telegram'] = 'not_configured'
        
        # Check Email
        if settings.EMAIL_HOST:
            channels['email'] = 'configured'
        else:
            channels['email'] = 'not_configured'
        
        return channels
    
    def _check_external_services(self):
        """Check external service connectivity."""
        external = {}
        
        # This would include checks for external APIs
        # For now, just return placeholder
        external['telegram_api'] = 'unknown'
        external['email_service'] = 'unknown'
        
        return external
    
    def _get_configuration_status(self):
        """Get configuration status."""
        return {
            'debug_mode': settings.DEBUG,
            'cache_configured': bool(settings.CACHES.get('default')),
            'celery_configured': bool(getattr(settings, 'CELERY_BROKER_URL', None)),
            'logging_configured': bool(settings.LOGGING),
        }
