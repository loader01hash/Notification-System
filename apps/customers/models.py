"""
Customer models for the notification system.
"""
from django.db import models
import uuid


class Customer(models.Model):
    """Customer model for managing customer data."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    telegram_chat_id = models.CharField(max_length=50, blank=True)
    
    # Address information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Account status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
        ordering = ['name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    @property
    def full_address(self):
        """Get formatted full address."""
        parts = [self.address, self.city, self.postal_code, self.country]
        return ', '.join(filter(None, parts))
    
    def get_notification_channels(self):
        """Get available notification channels for this customer."""
        channels = []
        if self.email:
            channels.append('email')
        if self.telegram_chat_id:
            channels.append('telegram')
        return channels
