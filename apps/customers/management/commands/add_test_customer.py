"""
Simple command to add a test customer.
"""
from django.core.management.base import BaseCommand
from apps.customers.models import Customer

class Command(BaseCommand):
    help = 'Add a test customer'

    def handle(self, *args, **options):
        """Add test customer."""
        
        customer_data = {
            'name': 'Test Customer',
            'email': 'test@example.com',
            'phone': '+1234567890',
            'telegram_chat_id': '123456789',
            'address': '123 Test Street',
            'city': 'Test City',
            'country': 'Test Country',
            'postal_code': '12345',
            'is_active': True,
            'is_verified': True
        }
        
        customer, created = Customer.objects.get_or_create(
            email=customer_data['email'],
            defaults=customer_data
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created customer: {customer.name} ({customer.email})')
            )
        else:
            self.stdout.write(f'Customer already exists: {customer.name}')
        
        # Show all customers
        total = Customer.objects.count()
        self.stdout.write(f'\nTotal customers in database: {total}')
        
        for c in Customer.objects.all()[:5]:
            self.stdout.write(f'  - {c.name} ({c.email})')
        
        self.stdout.write('\n✅ Test customer setup complete!')
