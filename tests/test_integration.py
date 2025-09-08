"""
Integration Tests for Notification System
=========================================

This module contains integration tests that verify the complete notification
workflow from order status changes to notification delivery.
"""
from django.test import TestCase, TransactionTestCase
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.utils import timezone

from apps.orders.models import Order
from apps.customers.models import Customer
from apps.notifications.models import Notification, NotificationTemplate, NotificationPreference
from apps.notifications.services import NotificationService


class NotificationIntegrationTest(TransactionTestCase):
    """Integration tests for the complete notification workflow."""
    
    def setUp(self):
        """Set up test data."""
        # Create test customer
        self.customer = Customer.objects.create(
            name='Integration Test Customer',
            email='test@example.com',
            phone='+1234567890',
            telegram_chat_id='123456789',
            address='123 Test Street',
            city='Test City',
            country='Test Country',
            postal_code='12345'
        )
        
        # Create notification preferences
        self.preferences = NotificationPreference.objects.create(
            customer=self.customer,
            email_enabled=True,
            telegram_enabled=True
        )
        
        # Create notification templates
        self.email_template = NotificationTemplate.objects.create(
            name='order_update_email',
            channel='email',
            subject_template='Order Update: {{ order_id }}',
            body_template='Dear {{ customer_name }}, your order {{ order_id }} status changed from {{ old_status }} to {{ new_status }}.',
            is_active=True
        )
        
        self.telegram_template = NotificationTemplate.objects.create(
            name='order_update_telegram',
            channel='telegram',
            subject_template='Order Update',
            body_template='🔔 Order {{ order_id }} for {{ customer_name }} is now {{ new_status }}!',
            is_active=True
        )
    
    def test_notification_service_template_rendering(self):
        """Test that NotificationService correctly renders templates."""
        service = NotificationService()
        
        context = {
            'customer_name': 'Integration Test Customer',
            'order_id': 'TEST-001',
            'old_status': 'pending',
            'new_status': 'SUCCESS'
        }
        
        notification = service.create_notification(
            template_name='order_update_email',
            recipient='test@example.com',
            customer=self.customer,
            context=context
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.subject, 'Order Update: TEST-001')
        self.assertIn('Integration Test Customer', notification.message)
        self.assertIn('TEST-001', notification.message)
        self.assertIn('SUCCESS', notification.message)
        
        # Verify no template variables remain unrendered
        self.assertNotIn('{{', notification.subject)
        self.assertNotIn('{{', notification.message)
        self.assertNotIn('}}', notification.subject)
        self.assertNotIn('}}', notification.message)
