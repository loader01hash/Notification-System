#!/usr/bin/env python
"""
Order API Testing and Debugging Guide
=====================================

This script will help you test the Order API and debug notification issues.
"""
import os
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.orders.models import Order
from apps.customers.models import Customer
from django.contrib.auth.models import User

BASE_URL = "http://localhost:8000"

def check_database_status():
    """Check the current state of the database"""
    print("🔍 DATABASE STATUS")
    print("=" * 50)
    
    # Check customers
    customers = Customer.objects.all()
    print(f"📋 Customers: {customers.count()}")
    for customer in customers[:3]:
        print(f"  - {customer.name} ({customer.email})")
        print(f"    Telegram: {customer.telegram_chat_id or 'Not set'}")
        print(f"    Phone: {customer.phone or 'Not set'}")
    
    # Check orders
    orders = Order.objects.all()
    print(f"\n📦 Orders: {orders.count()}")
    for order in orders[:3]:
        print(f"  - Order #{order.order_number}: {order.status}")
        print(f"    Customer: {order.customer.name}")
        print(f"    Total: ${order.total_amount}")
        print(f"    ID: {order.id}")
    
    return orders

def check_order_api_endpoints():
    """Display available order API endpoints"""
    print("\n🚀 ORDER API ENDPOINTS")
    print("=" * 50)
    
    endpoints = [
        {
            "method": "GET",
            "url": "/api/v1/orders/",
            "description": "List all orders",
            "auth_required": True
        },
        {
            "method": "POST", 
            "url": "/api/v1/orders/",
            "description": "Create new order",
            "auth_required": True
        },
        {
            "method": "GET",
            "url": "/api/v1/orders/{id}/",
            "description": "Get specific order details",
            "auth_required": True
        },
        {
            "method": "PUT",
            "url": "/api/v1/orders/{id}/",
            "description": "Update entire order (triggers notifications)",
            "auth_required": True
        },
        {
            "method": "PATCH",
            "url": "/api/v1/orders/{id}/",
            "description": "Partially update order (triggers notifications)",
            "auth_required": True
        },
        {
            "method": "PUT",
            "url": "/api/v1/orders/{id}/status/",
            "description": "Update only order status (triggers notifications)",
            "auth_required": True
        },
        {
            "method": "DELETE",
            "url": "/api/v1/orders/{id}/",
            "description": "Delete order",
            "auth_required": True
        }
    ]
    
    for endpoint in endpoints:
        print(f"🔹 {endpoint['method']} {endpoint['url']}")
        print(f"   {endpoint['description']}")
        if endpoint['auth_required']:
            print("   🔐 Requires Authentication")
        print()

def show_notification_flow():
    """Show how notifications are triggered"""
    print("🔔 NOTIFICATION FLOW")
    print("=" * 50)
    
    flow_steps = [
        "1. 📝 API Call: PUT /api/v1/orders/{id}/ or PUT /api/v1/orders/{id}/status/",
        "2. 🔄 Order.update_status() method is called",
        "3. 🚀 _trigger_status_notification() triggers Celery task",
        "4. ⚙️  send_order_update_notification.delay() queues the task",
        "5. 📧 Email notification sent via SMTP",
        "6. 📱 Telegram notification sent via Bot API",
        "7. 📊 Notification records saved to database"
    ]
    
    for step in flow_steps:
        print(step)
    
    print("\n💡 NOTIFICATION REQUIREMENTS:")
    print("   - Customer must have email address (for email notifications)")
    print("   - Customer must have telegram_chat_id (for Telegram notifications)")
    print("   - Celery worker must be running")
    print("   - Redis must be running")
    print("   - Valid tokens in .env file")

def create_test_curl_commands(order_id=None):
    """Generate curl commands for testing"""
    print("\n🧪 TEST COMMANDS")
    print("=" * 50)
    
    if order_id:
        print(f"🎯 Testing with Order ID: {order_id}")
        print()
        
        # Test order details
        print("📋 Get Order Details:")
        print(f"""curl -X GET "{BASE_URL}/api/v1/orders/{order_id}/" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Token YOUR_TOKEN_HERE"
""")
        
        # Test status update
        print("📦 Update Order Status (Triggers Notifications):")
        print(f"""curl -X PUT "{BASE_URL}/api/v1/orders/{order_id}/status/" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Token YOUR_TOKEN_HERE" \\
  -d '{{"status": "delivered"}}'
""")
        
        # Test full order update
        print("📝 Update Full Order (Triggers Notifications):")
        print(f"""curl -X PATCH "{BASE_URL}/api/v1/orders/{order_id}/" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Token YOUR_TOKEN_HERE" \\
  -d '{{"status": "shipped", "tracking_number": "TRACK123"}}'
""")
        
    else:
        print("❌ No orders found. Create an order first:")
        print(f"""curl -X POST "{BASE_URL}/api/v1/orders/" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Token YOUR_TOKEN_HERE" \\
  -d '{{
    "order_number": "ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    "customer": "CUSTOMER_UUID_HERE",
    "total_amount": "99.99",
    "shipping_address": "123 Test St, Test City, TC 12345",
    "status": "pending"
  }}'
""")

def check_celery_tasks():
    """Show Celery task status"""
    print("\n⚙️  CELERY TASKS")
    print("=" * 50)
    
    print("📋 Available notification tasks:")
    tasks = [
        "send_order_update_notification - Main order notification task",
        "send_notification_task - Generic notification sender", 
        "send_bulk_notifications_task - Bulk notification sender",
        "retry_failed_notifications - Retry failed notifications",
        "cleanup_old_notifications - Cleanup old records"
    ]
    
    for task in tasks:
        print(f"  🔹 {task}")
    
    print("\n🚀 Task Triggers:")
    print("  - Order status change → send_order_update_notification")
    print("  - Manual notification → send_notification_task")
    print("  - Bulk operations → send_bulk_notifications_task")

def check_environment_config():
    """Check .env configuration"""
    print("\n🔧 ENVIRONMENT CONFIG")
    print("=" * 50)
    
    from decouple import config
    
    configs = {
        "TELEGRAM_BOT_TOKEN": config('TELEGRAM_BOT_TOKEN', default='Not set'),
        "TELEGRAM_CHAT_ID": config('TELEGRAM_CHAT_ID', default='Not set'),
        "EMAIL_HOST_USER": config('EMAIL_HOST_USER', default='Not set'),
        "EMAIL_HOST_PASSWORD": config('EMAIL_HOST_PASSWORD', default='Not set'),
        "REDIS_URL": config('REDIS_URL', default='redis://localhost:6379/0'),
    }
    
    for key, value in configs.items():
        status = "✅" if value != "Not set" and value != "" else "❌"
        display_value = value if key != "EMAIL_HOST_PASSWORD" else "*" * len(value) if value != "Not set" else "Not set"
        display_value = display_value if key != "TELEGRAM_BOT_TOKEN" else value[:10] + "..." if value != "Not set" else "Not set"
        print(f"  {status} {key}: {display_value}")

def debug_notifications():
    """Debug notification system"""
    print("\n🐛 NOTIFICATION DEBUGGING")
    print("=" * 50)
    
    from apps.notifications.models import NotificationTemplate, Notification
    
    # Check templates
    templates = NotificationTemplate.objects.all()
    print(f"📝 Notification Templates: {templates.count()}")
    for template in templates:
        print(f"  - {template.name} ({template.channel})")
    
    # Check recent notifications
    notifications = Notification.objects.all().order_by('-created_at')[:5]
    print(f"\n📬 Recent Notifications: {notifications.count()}")
    for notif in notifications:
        print(f"  - {notif.template_name} → {notif.recipient} ({notif.status})")
        print(f"    Created: {notif.created_at}")

def main():
    """Main function"""
    print("🔍 ORDER API TESTING & DEBUGGING GUIDE")
    print("=" * 60)
    print(f"🕐 Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check database
    orders = check_database_status()
    
    # Show API endpoints
    check_order_api_endpoints()
    
    # Show notification flow
    show_notification_flow()
    
    # Generate test commands
    first_order = orders.first() if orders.exists() else None
    order_id = first_order.id if first_order else None
    create_test_curl_commands(order_id)
    
    # Check Celery
    check_celery_tasks()
    
    # Check environment
    check_environment_config()
    
    # Debug notifications
    debug_notifications()
    
    print("\n🎯 NEXT STEPS:")
    print("=" * 50)
    print("1. ✅ Ensure both Django server and Celery worker are running")
    print("2. ✅ Test API endpoints using the curl commands above")
    print("3. ✅ Check Celery worker logs for task execution")
    print("4. ✅ Verify notifications are sent to Telegram and Email")
    print("5. ✅ Check notification records in database")

if __name__ == '__main__':
    main()
