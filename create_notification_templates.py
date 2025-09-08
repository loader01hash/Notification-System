#!/usr/bin/env python
"""
Script to create notification templates for the system.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from apps.notifications.models import NotificationTemplate

def create_templates():
    """Create notification templates for different channels and purposes."""
    
    templates = [
        # Email templates
        {
            'name': 'order_update_email',
            'channel': 'email',
            'subject_template': 'Order Update: #{{ order_id }}',
            'body_template': '''Dear {{ customer_name }},

Your order #{{ order_id }} has been updated!

Order Details:
- Order Number: {{ order_id }}
- Status: {{ new_status }}
- Total Amount: ${{ order_total }}
- Order Date: {{ order_date }}

Status Change: {{ old_status }} to {{ new_status }}

Thank you for your business!

Best regards,
The Notification System Team'''.strip()
        },
        
        # Telegram templates
        {
            'name': 'order_update_telegram',
            'channel': 'telegram',
            'subject_template': '📦 Order Update',
            'body_template': '''🔔 *Order Update Notification*

👤 Customer: {{ customer_name }}
📦 Order: #{{ order_id }}
💰 Total: ${{ order_total }}
📅 Date: {{ order_date }}

📊 Status: {{ old_status }} ➡️ *{{ new_status }}*

🚀 Thank you for choosing our service!'''.strip()
        },
        
        # Welcome email template
        {
            'name': 'welcome_email',
            'channel': 'email',
            'subject_template': 'Welcome to Notification System!',
            'body_template': '''Dear {{ customer_name }},

Welcome to our Notification System!

We're excited to have you on board. You'll receive notifications about:
- Order updates
- Important announcements
- System notifications

You can manage your notification preferences at any time.

Best regards,
The Notification System Team'''.strip()
        },
        
        # Test notification template
        {
            'name': 'test_notification',
            'channel': 'telegram',
            'subject_template': '🧪 Test Notification',
            'body_template': '''🧪 *Test Notification*

This is a test message to verify that your Telegram bot is working correctly.

✅ If you receive this message, your notification system is set up properly!

📱 Sent at: {{ timestamp }}'''.strip()
        }
    ]
    
    created_count = 0
    
    for template_data in templates:
        template, created = NotificationTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )
        
        if created:
            print(f"✅ Created template: {template.name} ({template.channel})")
            created_count += 1
        else:
            print(f"ℹ️  Template already exists: {template.name}")
    
    print(f"\n🎉 Template creation complete! Created {created_count} new templates.")
    print(f"📊 Total templates in database: {NotificationTemplate.objects.count()}")

if __name__ == '__main__':
    create_templates()
