"""
Tests for notification models and services.
"""
from django.test import TestCase
from django.utils import timezone
from apps.notifications.models import NotificationTemplate, Notification
from apps.notifications.services import NotificationService
from apps.customers.models import Customer
from apps.orders.models import Order
from decimal import Decimal


class NotificationTemplateTest(TestCase):
    """Test cases for NotificationTemplate model."""
    
    def setUp(self):
        """Set up test data."""
        self.template_data = {
            'name': 'test_template',
            'channel': 'email',
            'subject_template': 'Test Subject: {{ customer_name }}',
            'body_template': 'Hello {{ customer_name }}, order {{ order_id }} is {{ new_status }}.',
        }
    
    def test_create_template(self):
        """Test creating a notification template."""
        template = NotificationTemplate.objects.create(**self.template_data)
        
        self.assertEqual(template.name, 'test_template')
        self.assertEqual(template.channel, 'email')
        self.assertTrue(template.is_active)
        self.assertIn('{{ customer_name }}', template.subject_template)
        self.assertIn('{{ order_id }}', template.body_template)


class NotificationServiceTest(TestCase):
    """Test cases for NotificationService."""
    
    def setUp(self):
        """Set up test data."""
        self.customer = Customer.objects.create(
            name='Test Customer',
            email='test@example.com',
            telegram_chat_id='123456789'
        )
        
        self.order = Order.objects.create(
            customer=self.customer,
            order_number='TEST-001',
            total_amount=Decimal('99.99'),
            status='pending'
        )
        
        self.template = NotificationTemplate.objects.create(
            name='test_order_update',
            channel='email',
            subject_template='Order Update: {{ order_id }}',
            body_template='Hi {{ customer_name }}, your order {{ order_id }} is now {{ new_status }}.'
        )
    
    def test_create_notification(self):
        """Test creating a notification through the service."""
        service = NotificationService()
        
        context = {
            'customer_name': self.customer.name,
            'order_id': self.order.order_number,
            'new_status': 'shipped'
        }
        
        notification = service.create_notification(
            template_name='test_order_update',
            recipient=self.customer.email,
            customer=self.customer,
            order=self.order,
            context=context
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.customer, self.customer)
        self.assertEqual(notification.template.channel, 'email')
        self.assertIn('Test Customer', notification.message)
        self.assertIn('TEST-001', notification.message)
        self.assertIn('shipped', notification.message)


class NotificationModelTest(TestCase):
    """Test cases for Notification model."""
    
    def setUp(self):
        """Set up test data."""
        self.customer = Customer.objects.create(
            name='Test Customer',
            email='test@example.com'
        )
        
        self.template = NotificationTemplate.objects.create(
            name='test_template',
            channel='email',
            subject_template='Test Subject',
            body_template='Test message body'
        )
    
    def test_notification_creation(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            template=self.template,
            recipient='test@example.com',
            subject='Test Subject',
            message='Test message body',
            customer=self.customer,
            status='pending'
        )
        
        self.assertEqual(notification.customer, self.customer)
        self.assertEqual(notification.template.channel, 'email')
        self.assertEqual(notification.status, 'pending')
        self.assertIsNotNone(notification.created_at)
