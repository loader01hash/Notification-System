"""
Management command to sync existing users to customer records.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.customers.models import Customer


class Command(BaseCommand):
    help = 'Sync existing users to customer records'

    def handle(self, *args, **options):
        """Sync users to customers."""
        users = User.objects.all()
        created_count = 0
        
        for user in users:
            # Check if customer already exists for this user's email
            if not Customer.objects.filter(email=user.email).exists():
                customer_name = f"{user.first_name} {user.last_name}".strip() or user.username
                customer_email = user.email or f"{user.username}@example.com"
                
                customer = Customer.objects.create(
                    name=customer_name,
                    email=customer_email,
                    is_active=True,
                    is_verified=user.is_active
                )
                
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created customer: {customer.name} ({customer.email}) '
                        f'for user: {user.username}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Customer already exists for user: {user.username} ({user.email})'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} customer records'
            )
        )
