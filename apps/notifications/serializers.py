"""
Notification API serializers.
"""
from rest_framework import serializers
from .models import Notification, NotificationTemplate, NotificationPreference


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates."""
    
    class Meta:
        model = NotificationTemplate
        fields = ['id', 'name', 'channel', 'subject_template', 'body_template', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    channel = serializers.CharField(source='template.channel', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'template_name', 'channel', 'recipient', 'subject', 'message',
            'status', 'priority', 'retry_count', 'max_retries', 'error_message',
            'created_at', 'updated_at', 'scheduled_at', 'sent_at', 'delivered_at',
            'customer_name', 'order_number'
        ]
        read_only_fields = [
            'id', 'template_name', 'channel', 'created_at', 'updated_at',
            'sent_at', 'delivered_at', 'customer_name', 'order_number'
        ]


class SendNotificationSerializer(serializers.Serializer):
    """Serializer for sending notifications."""
    
    template_name = serializers.CharField(max_length=100)
    recipient = serializers.CharField(max_length=255)
    context = serializers.JSONField(required=False, default=dict)
    priority = serializers.ChoiceField(
        choices=['low', 'normal', 'high', 'urgent'],
        default='normal'
    )
    scheduled_at = serializers.DateTimeField(required=False)
    customer_id = serializers.UUIDField(required=False)
    order_id = serializers.UUIDField(required=False)
    
    def validate_template_name(self, value):
        """Validate that template exists and is active."""
        try:
            NotificationTemplate.objects.get(name=value, is_active=True)
        except NotificationTemplate.DoesNotExist:
            raise serializers.ValidationError(f"Template '{value}' not found or inactive")
        return value


class SendBulkNotificationSerializer(serializers.Serializer):
    """Serializer for sending bulk notifications."""
    
    template_name = serializers.CharField(max_length=100)
    recipients = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=100
    )
    context = serializers.JSONField(required=False, default=dict)
    priority = serializers.ChoiceField(
        choices=['low', 'normal', 'high', 'urgent'],
        default='normal'
    )
    
    def validate_template_name(self, value):
        """Validate that template exists and is active."""
        try:
            NotificationTemplate.objects.get(name=value, is_active=True)
        except NotificationTemplate.DoesNotExist:
            raise serializers.ValidationError(f"Template '{value}' not found or inactive")
        return value
    
    def validate_recipients(self, value):
        """Validate recipients data."""
        for i, recipient_data in enumerate(value):
            if 'recipient' not in recipient_data:
                raise serializers.ValidationError(f"Recipient {i}: 'recipient' field is required")
        return value


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences."""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'email_enabled', 'telegram_enabled',
            'order_updates', 'promotional', 'security_alerts',
            'quiet_hours_start', 'quiet_hours_end', 'timezone'
        ]
