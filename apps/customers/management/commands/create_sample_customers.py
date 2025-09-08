"""
Django management command to create sample customers for testing.
"""
from django.core.management.base import BaseCommand
from apps.customers.models import Customer
from apps.notifications.models import NotificationPreference


class Command(BaseCommand):
    help = 'Create sample customers for testing'

    def handle(self, *args, **options):
        """Create sample customers."""
        
        self.stdout.write("Creating sample customers...")
        
        # Sample customers data
        customers_data = [
            {
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'phone': '+1234567890',
                'telegram_chat_id': '123456789',
                'address': '123 Main St',
                'city': 'New York',
                'country': 'USA',
                'postal_code': '10001',
                'is_verified': True
            },
            {
                'name': 'Jane Smith',
                'email': 'jane.smith@example.com',
                'phone': '+1987654321',
                'address': '456 Oak Ave',
                'city': 'Los Angeles',
                'country': 'USA',
                'postal_code': '90210',
                'is_verified': True
            },
            {
                'name': 'Bob Johnson',
                'email': 'bob.johnson@example.com',
                'phone': '+1555123456',
                'telegram_chat_id': '987654321',
                'address': '789 Pine St',
                'city': 'Chicago',
                'country': 'USA',
                'postal_code': '60601'
            },
            {
                'name': 'Alice Brown',
                'email': 'alice.brown@example.com',
                'address': '321 Elm St',
                'city': 'Houston',
                'country': 'USA',
                'postal_code': '77001',
                'is_verified': True
            },
            {
                'name': 'Demo User',
                'email': 'demo@example.com',
                'phone': '+1111222333',
                'telegram_chat_id': '111222333',
                'address': '999 Demo Lane',
                'city': 'Demo City',
                'country': 'Demo Country',
                'postal_code': '00000',
                'is_verified': True
            }
        ]
        
        created_count = 0
        
        for customer_data in customers_data:
            customer, created = Customer.objects.get_or_create(
                email=customer_data['email'],
                defaults=customer_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"Created customer: {customer.name} ({customer.email})")
                
                # Create default notification preferences
                preferences, pref_created = NotificationPreference.objects.get_or_create(
                    customer=customer,
                    defaults={
                        'email_enabled': True,
                        'telegram_enabled': bool(customer.telegram_chat_id),
                        'order_updates': True,
                        'promotional': False,
                        'security_alerts': True,
                        'timezone': 'UTC'
                    }
                )
                
                if pref_created:
                    self.stdout.write(f"  Created preferences for {customer.name}")
            else:
                self.stdout.write(f"Customer already exists: {customer.name}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_count} new customers. '
                f'Total customers: {Customer.objects.count()}'
            )
        )
