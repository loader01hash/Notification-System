"""
Notification models for the notification system.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class NotificationTemplate(models.Model):
    """Template for notification messages."""
    
    CHANNEL_CHOICES = [
        ('telegram', 'Telegram'),
        ('email', 'Email'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    subject_template = models.CharField(max_length=200, blank=True)
    body_template = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.channel})"


class Notification(models.Model):
    """Individual notification record."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    recipient = models.CharField(max_length=255)  # Email, phone, telegram chat_id, etc.
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Metadata
    context_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Foreign keys
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['template', 'status']),
        ]
    
    def __str__(self):
        return f"Notification {self.id} - {self.template.name} to {self.recipient}"
    
    def can_retry(self):
        """Check if notification can be retried."""
        return self.retry_count < self.max_retries and self.status == 'failed'
    
    def mark_as_sent(self):
        """Mark notification as sent."""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at', 'updated_at'])
    
    def mark_as_delivered(self):
        """Mark notification as delivered."""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at', 'updated_at'])
    
    def mark_as_failed(self, error_message=None):
        """Mark notification as failed."""
        self.status = 'failed'
        if error_message:
            self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'updated_at'])
    
    def increment_retry(self):
        """Increment retry count."""
        self.retry_count += 1
        self.status = 'retrying'
        self.save(update_fields=['retry_count', 'status', 'updated_at'])


class NotificationLog(models.Model):
    """Log of notification delivery attempts."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='logs')
    attempt_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20)
    response_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Log {self.id} - Attempt {self.attempt_number} for {self.notification.id}"


class NotificationPreference(models.Model):
    """User notification preferences."""
    
    customer = models.OneToOneField('customers.Customer', on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Channel preferences
    email_enabled = models.BooleanField(default=True)
    telegram_enabled = models.BooleanField(default=True)
    
    # Notification type preferences
    order_updates = models.BooleanField(default=True)
    promotional = models.BooleanField(default=False)
    security_alerts = models.BooleanField(default=True)
    
    # Timing preferences
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
    
    def __str__(self):
        return f"Preferences for {self.customer}"
