"""
Django management command to manage user roles
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.auth_system.models import UserRole, make_user_admin, remove_admin_role, is_user_admin


class Command(BaseCommand):
    help = 'Manage user roles (admin/user)'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['make_admin', 'remove_admin', 'check', 'list_admins', 'setup_demo'],
            help='Action to perform'
        )
        parser.add_argument(
            '--username',
            help='Username to modify (required for make_admin, remove_admin, check)'
        )

    def handle(self, *args, **options):
        action = options['action']
        username = options.get('username')

        if action == 'make_admin':
            if not username:
                self.stdout.write(
                    self.style.ERROR('Username is required for make_admin action')
                )
                return
            
            success, message = make_user_admin(username)
            if success:
                self.stdout.write(self.style.SUCCESS(message))
            else:
                self.stdout.write(self.style.ERROR(message))

        elif action == 'remove_admin':
            if not username:
                self.stdout.write(
                    self.style.ERROR('Username is required for remove_admin action')
                )
                return
            
            success, message = remove_admin_role(username)
            if success:
                self.stdout.write(self.style.SUCCESS(message))
            else:
                self.stdout.write(self.style.ERROR(message))

        elif action == 'check':
            if not username:
                self.stdout.write(
                    self.style.ERROR('Username is required for check action')
                )
                return
            
            is_admin = is_user_admin(username)
            status = "Admin" if is_admin else "Regular User"
            self.stdout.write(
                self.style.SUCCESS(f"User '{username}' has {status} privileges")
            )

        elif action == 'list_admins':
            self.stdout.write(self.style.SUCCESS("Current Admin Users:"))
            self.stdout.write("-" * 40)
            
            # Staff users
            staff_users = User.objects.filter(is_staff=True)
            for user in staff_users:
                self.stdout.write(f"• {user.username} (Django Staff)")
            
            # Role-based admins
            admin_roles = UserRole.objects.filter(role='admin')
            for role in admin_roles:
                self.stdout.write(f"• {role.user.username} (Role-based Admin)")
            
            # Special user
            try:
                special_user = User.objects.get(username='krushnappan')
                self.stdout.write(f"• {special_user.username} (Special Admin)")
            except User.DoesNotExist:
                pass

        elif action == 'setup_demo':
            self.stdout.write(self.style.SUCCESS("Setting up demo users with proper roles..."))
            
            # Create/update demo_admin user
            demo_admin, created = User.objects.get_or_create(
                username='demo_admin',
                defaults={
                    'email': 'admin@company.com',
                    'first_name': 'System',
                    'last_name': 'Administrator',
                }
            )
            
            if created:
                demo_admin.set_password('admin123')
                demo_admin.save()
                self.stdout.write(f"✅ Created demo_admin user")
            else:
                self.stdout.write(f"ℹ️  demo_admin user already exists")
            
            # Make demo_admin an admin
            success, message = make_user_admin(demo_admin)
            self.stdout.write(self.style.SUCCESS(f"✅ {message}"))
            
            # Create/update demo_customer user
            demo_customer, created = User.objects.get_or_create(
                username='demo_customer',
                defaults={
                    'email': 'customer@example.com',
                    'first_name': 'John',
                    'last_name': 'Customer',
                }
            )
            
            if created:
                demo_customer.set_password('user123')
                demo_customer.save()
                self.stdout.write(f"✅ Created demo_customer user")
            else:
                self.stdout.write(f"ℹ️  demo_customer user already exists")
            
            # Ensure demo_customer is regular user
            from apps.auth_system.models import ensure_user_role
            role = ensure_user_role(demo_customer)
            if role.role != 'user':
                role.role = 'user'
                role.save()
            self.stdout.write(f"✅ demo_customer set as regular user")
            
            # Create krushnappan user if it doesn't exist
            krushnappan, created = User.objects.get_or_create(
                username='krushnappan',
                defaults={
                    'email': 'krushnappanm@gmail.com',
                    'first_name': 'Krushna',
                    'last_name': 'Ppan',
                    'is_staff': True,
                }
            )
            
            if created:
                krushnappan.set_password('admin123')
                krushnappan.save()
                self.stdout.write(f"✅ Created krushnappan user")
            else:
                if not krushnappan.is_staff:
                    krushnappan.is_staff = True
                    krushnappan.save()
                self.stdout.write(f"ℹ️  krushnappan user already exists (ensured staff status)")
            
            self.stdout.write("\n" + "="*50)
            self.stdout.write(self.style.SUCCESS("Demo setup completed! Available users:"))
            self.stdout.write("Admin Users:")
            self.stdout.write("  • demo_admin (password: admin123) - Role-based admin")
            self.stdout.write("  • krushnappan (password: admin123) - Django staff admin")
            self.stdout.write("Regular Users:")
            self.stdout.write("  • demo_customer (password: user123) - Regular user")
            self.stdout.write("="*50)
