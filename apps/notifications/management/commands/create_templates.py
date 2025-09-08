"""
Management command to create default notification templates.
"""
from django.core.management.base import BaseCommand
from apps.notifications.models import NotificationTemplate


class Command(BaseCommand):
    help = 'Create default notification templates'
    
    def handle(self, *args, **options):
        """Create default templates."""
        templates = [
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
            {
                'name': 'order_update_telegram',
                'channel': 'telegram',
                'subject_template': '📦 Order Update',
                'body_template': '''� *Order Update Notification*

👤 Customer: {{ customer_name }}
📦 Order: #{{ order_id }}
💰 Total: ${{ order_total }}
📅 Date: {{ order_date }}

📊 Status: {{ old_status }} ➡️ *{{ new_status }}*

🚀 Thank you for choosing our service!'''.strip()
            },
            {
                'name': 'welcome_email',
                'channel': 'email',
                'subject_template': 'Welcome to Notification System, {{ customer_name }}!',
                'body_template': '''
Dear {{ customer_name }},

Welcome to our notification system! We're excited to have you on board.

You'll receive timely updates about your orders and important account information.

To manage your notification preferences, visit your account settings.

Best regards,
Notification System Team
                '''.strip()
            },
            {
                'name': 'order_confirmation_email',
                'channel': 'email',
                'subject_template': 'Order Confirmation: {{ order_id }}',
                'body_template': '''
Dear {{ customer_name }},

Thank you for your order! We've received your order and it's being processed.

Order Details:
- Order Number: {{ order_id }}
- Total Amount: {{ order_total }}
- Order Date: {{ order_date }}

We'll send you updates as your order progresses.

Best regards,
Notification System Team
                '''.strip()
            }
        ]
        
        created_count = 0
        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Template already exists: {template.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new templates')
        )
