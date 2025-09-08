"""
Order models for the notification system.
"""
from django.db import models
from decimal import Decimal
import uuid


class Order(models.Model):
    """Order model for managing customer orders."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='orders')
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Shipping information
    shipping_address = models.TextField()
    shipping_method = models.CharField(max_length=50, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer.name}"
    
    def update_status(self, new_status, save=True):
        """Update order status and set appropriate timestamps."""
        old_status = self.status
        self.status = new_status
        
        # Set timestamps based on status
        from django.utils import timezone
        now = timezone.now()
        
        if new_status == 'confirmed' and not self.confirmed_at:
            self.confirmed_at = now
        elif new_status == 'shipped' and not self.shipped_at:
            self.shipped_at = now
        elif new_status == 'delivered' and not self.delivered_at:
            self.delivered_at = now
        
        if save:
            self.save()
        
        # Trigger notification if status changed
        if old_status != new_status:
            self._trigger_status_notification(old_status, new_status)
    
    def _trigger_status_notification(self, old_status, new_status):
        """Trigger notification for status change."""
        try:
            # Import here to avoid circular imports
            from apps.notifications.tasks import send_order_update_notification
            
            # Queue the task asynchronously with proper error handling
            result = send_order_update_notification.apply_async(
                args=[str(self.id), old_status, new_status],
                countdown=2,  # 2 second delay to ensure transaction commit
                retry=True,
                retry_policy={
                    'max_retries': 3,
                    'interval_start': 0,
                    'interval_step': 0.2,
                    'interval_max': 0.2,
                }
            )
            print(f"Queued notification task: {result.id}")
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Celery task queuing failed: {e}")
            
            # Fallback to direct execution
            try:
                from apps.notifications.tasks import send_order_update_notification
                logger.info("Falling back to direct execution...")
                send_order_update_notification(str(self.id), old_status, new_status)
                logger.info("Direct notification execution successful")
            except Exception as fallback_error:
                logger.error(f"Direct execution also failed: {fallback_error}")


class OrderItem(models.Model):
    """Individual items in an order."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    
    # Product information
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional details
    product_details = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        """Calculate total price before saving."""
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
