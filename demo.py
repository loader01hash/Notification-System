"""
Demonstration script for the Django Notification System.

This script demonstrates the key features and capabilities of the notification system.
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.customers.models import Customer
from apps.orders.models import Order, OrderItem
from apps.notifications.models import NotificationTemplate, Notification
from apps.notifications.services import NotificationService
from apps.notifications.tasks import send_order_update_notification


def create_demo_data():
    """Create demo customers and orders."""
    print("🎭 Creating demo data...")
    
    # Create demo customers
    customers = [
        {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'telegram_chat_id': '123456789',
            'address': '123 Main St',
            'city': 'New York',
            'country': 'USA',
            'postal_code': '10001'
        },
        {
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'phone': '+0987654321',
            'telegram_chat_id': '987654321',
            'address': '456 Oak Ave',
            'city': 'Los Angeles',
            'country': 'USA',
            'postal_code': '90001'
        }
    ]
    
    created_customers = []
    for customer_data in customers:
        customer, created = Customer.objects.get_or_create(
            email=customer_data['email'],
            defaults=customer_data
        )
        created_customers.append(customer)
        if created:
            print(f"✅ Created customer: {customer.name}")
        else:
            print(f"ℹ️ Customer already exists: {customer.name}")
    
    # Create demo orders
    for i, customer in enumerate(created_customers):
        order_data = {
            'order_number': f'ORD-{1000 + i}',
            'customer': customer,
            'total_amount': Decimal('99.99'),
            'shipping_address': customer.full_address,
            'status': 'pending'
        }
        
        order, created = Order.objects.get_or_create(
            order_number=order_data['order_number'],
            defaults=order_data
        )
        
        if created:
            # Create order items
            OrderItem.objects.create(
                order=order,
                product_name=f'Demo Product {i + 1}',
                product_sku=f'SKU-{i + 1}',
                quantity=1,
                unit_price=Decimal('99.99')
            )
            print(f"✅ Created order: {order.order_number}")
        else:
            print(f"ℹ️ Order already exists: {order.order_number}")
    
    return created_customers


def demonstrate_notification_creation():
    """Demonstrate creating and sending notifications."""
    print("\n📧 Demonstrating notification creation...")
    
    service = NotificationService()
    customers = Customer.objects.all()[:2]
    
    for customer in customers:
        # Create welcome notification
        welcome_notification = service.create_notification(
            template_name='welcome_email',
            recipient=customer.email,
            customer=customer,
            context={'customer_name': customer.name}
        )
        
        if welcome_notification:
            print(f"✅ Created welcome notification for {customer.name}")
        else:
            print(f"❌ Failed to create welcome notification for {customer.name}")


def demonstrate_order_workflow():
    """Demonstrate order status updates with notifications."""
    print("\n📦 Demonstrating order workflow...")
    
    orders = Order.objects.all()[:2]
    
    for order in orders:
        print(f"Processing order: {order.order_number}")
        
        # Simulate order status changes
        statuses = ['confirmed', 'processing', 'shipped', 'delivered']
        
        for status in statuses:
            order.update_status(status)
            print(f"  ✅ Updated order {order.order_number} to {status}")
            
            # This would trigger notification tasks in a real scenario
            # For demo, we'll create notifications directly
            service = NotificationService()
            
            # Email notification
            email_notification = service.create_notification(
                template_name='order_update_email',
                recipient=order.customer.email,
                customer=order.customer,
                order=order,
                context={
                    'customer_name': order.customer.name,
                    'order_id': order.order_number,
                    'order_status': order.status,
                    'order_total': str(order.total_amount),
                    'order_date': order.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            
            if email_notification:
                print(f"    📧 Created email notification for {order.customer.name}")
            
            # Telegram notification (if chat_id available)
            if order.customer.telegram_chat_id:
                telegram_notification = service.create_notification(
                    template_name='order_update_telegram',
                    recipient=order.customer.telegram_chat_id,
                    customer=order.customer,
                    order=order,
                    context={
                        'customer_name': order.customer.name,
                        'order_id': order.order_number,
                        'order_status': order.status,
                        'order_total': str(order.total_amount),
                        'order_date': order.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                )
                
                if telegram_notification:
                    print(f"    📱 Created Telegram notification for {order.customer.name}")


def demonstrate_bulk_notifications():
    """Demonstrate bulk notification sending."""
    print("\n📮 Demonstrating bulk notifications...")
    
    service = NotificationService()
    customers = Customer.objects.all()
    
    # Prepare recipients for bulk notification
    recipients = []
    for customer in customers:
        recipients.append({
            'recipient': customer.email,
            'customer': customer,
            'context': {
                'customer_name': customer.name
            }
        })
    
    # Send bulk welcome notifications
    notifications = service.send_bulk_notifications(
        template_name='welcome_email',
        recipients=recipients,
        context={'company_name': 'Demo Company'},
        priority='normal'
    )
    
    print(f"✅ Created {len(notifications)} bulk notifications")


def show_statistics():
    """Show notification statistics."""
    print("\n📊 Notification Statistics...")
    
    from apps.notifications.services import NotificationAnalyticsService
    
    stats = NotificationAnalyticsService.get_delivery_statistics(days=30)
    
    print(f"Total notifications: {stats['total']}")
    print(f"Sent: {stats['sent']}")
    print(f"Delivered: {stats['delivered']}")
    print(f"Failed: {stats['failed']}")
    print(f"Pending: {stats['pending']}")
    print(f"Success rate: {stats['success_rate']:.2f}%")
    
    print("\nBy channel:")
    for channel_stat in stats['by_channel']:
        print(f"  {channel_stat['template__channel']}: {channel_stat['count']}")


def demonstrate_advanced_features():
    """Demonstrate advanced features."""
    print("\n🔧 Demonstrating advanced features...")
    
    # Show available notification channels
    from core.patterns import NotificationChannelFactory
    factory = NotificationChannelFactory()
    channels = factory.get_available_channels()
    print(f"Available channels: {', '.join(channels)}")
    
    # Show templates
    templates = NotificationTemplate.objects.filter(is_active=True)
    print(f"Available templates: {', '.join([t.name for t in templates])}")
    
    # Show notification preferences (if any exist)
    from apps.notifications.models import NotificationPreference
    preferences_count = NotificationPreference.objects.count()
    print(f"Customer notification preferences configured: {preferences_count}")


def main():
    """Main demonstration function."""
    print("🚀 Django Notification System Demonstration")
    print("=" * 50)
    
    try:
        # Create demo data
        customers = create_demo_data()
        
        # Demonstrate features
        demonstrate_notification_creation()
        demonstrate_order_workflow()
        demonstrate_bulk_notifications()
        demonstrate_advanced_features()
        show_statistics()
        
        print("\n" + "=" * 50)
        print("✅ Demonstration completed successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("• Customer and order management")
        print("• Notification template system")
        print("• Multi-channel notification delivery")
        print("• Order workflow automation")
        print("• Bulk notification sending")
        print("• Analytics and reporting")
        print("• Design patterns implementation")
        
        print("\n🔧 To see notifications in action:")
        print("1. Configure Telegram bot token in .env")
        print("2. Configure email settings in .env")
        print("3. Start Celery worker: celery -A config worker -l info")
        print("4. Use the API endpoints to send real notifications")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
