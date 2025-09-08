"""
API Gateway serializers for system monitoring and health checks.
"""
from rest_framework import serializers


class HealthCheckSerializer(serializers.Serializer):
    """Serializer for health check response."""
    status = serializers.CharField()
    timestamp = serializers.FloatField()
    checks = serializers.DictField()


class SystemMetricsSerializer(serializers.Serializer):
    """Serializer for system metrics."""
    cpu_percent = serializers.FloatField(required=False, allow_null=True)
    memory_percent = serializers.FloatField(required=False, allow_null=True)
    disk_percent = serializers.FloatField(required=False, allow_null=True)
    load_average = serializers.FloatField(required=False, allow_null=True)
    error = serializers.CharField(required=False)


class CacheStatsSerializer(serializers.Serializer):
    """Serializer for cache statistics."""
    connected_clients = serializers.IntegerField(required=False)
    used_memory = serializers.IntegerField(required=False)
    hits = serializers.IntegerField(required=False)
    misses = serializers.IntegerField(required=False)
    error = serializers.CharField(required=False)


class DatabaseMetricsSerializer(serializers.Serializer):
    """Serializer for database metrics."""
    active_connections = serializers.CharField()


class ApplicationMetricsSerializer(serializers.Serializer):
    """Serializer for application metrics."""
    cache = CacheStatsSerializer()
    database_connections = DatabaseMetricsSerializer()
    error = serializers.CharField(required=False)


class MetricsSerializer(serializers.Serializer):
    """Serializer for metrics response."""
    timestamp = serializers.FloatField()
    system = SystemMetricsSerializer()
    application = ApplicationMetricsSerializer()


class NotificationChannelsSerializer(serializers.Serializer):
    """Serializer for notification channels status."""
    telegram = serializers.CharField()
    email = serializers.CharField()


class ExternalServicesSerializer(serializers.Serializer):
    """Serializer for external services status."""
    telegram_api = serializers.CharField()
    email_service = serializers.CharField()


class ServicesStatusSerializer(serializers.Serializer):
    """Serializer for services status."""
    notification_channels = NotificationChannelsSerializer()
    external = ExternalServicesSerializer()


class ConfigurationStatusSerializer(serializers.Serializer):
    """Serializer for configuration status."""
    debug_mode = serializers.BooleanField()
    cache_configured = serializers.BooleanField()
    celery_configured = serializers.BooleanField()
    logging_configured = serializers.BooleanField()


class SystemStatusSerializer(serializers.Serializer):
    """Serializer for system status response."""
    timestamp = serializers.FloatField()
    version = serializers.CharField()
    environment = serializers.CharField()
    services = ServicesStatusSerializer()
    configuration = ConfigurationStatusSerializer()