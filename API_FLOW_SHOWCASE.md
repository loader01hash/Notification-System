# API Flow Showcase - Django Notification System

## 🎯 Complete API Demonstration Flow

### Pre-Demo Setup Checklist
- [ ] Redis server running on localhost:6379
- [ ] Celery workers active
- [ ] Django server running on localhost:8000
- [ ] API documentation accessible at /api/docs/

---

## 🔄 API FLOW SEQUENCE

### 1. SYSTEM HEALTH & STATUS
```bash
# Check system health
curl -X GET http://localhost:8000/api/v1/health/

# Expected Response: 200 OK with system status
```

### 2. AUTHENTICATION FLOW
```bash
# Register new user
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "password": "secure_password123",
    "email": "demo@example.com",
    "first_name": "Demo",
    "last_name": "User"
  }'

# Get authentication token (regular user)
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "password": "secure_password123"
  }'

# 🔑 Get ADMIN authentication token (for restricted operations)
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "krushnappan",
    "password": "admin_password"
  }'

# Verify token (use token from previous response)
curl -X GET http://localhost:8000/api/v1/auth/token/check/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### 3. CUSTOMER MANAGEMENT
```bash
# Create customer
curl -X POST http://localhost:8000/api/v1/customers/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "telegram_chat_id": "123456789",
    "address": "123 Main St",
    "city": "New York",
    "country": "USA",
    "postal_code": "10001"
  }'

# List all customers
curl -X GET http://localhost:8000/api/v1/customers/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# Get specific customer (use customer ID from create response)
curl -X GET http://localhost:8000/api/v1/customers/CUSTOMER_ID/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# Update customer
curl -X PATCH http://localhost:8000/api/v1/customers/CUSTOMER_ID/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1987654321"
  }'
```

### 4. ORDER MANAGEMENT (Auto-triggers Notifications)

**📝 Note**: Customer is automatically assigned from authenticated user's email. Tracking number is auto-generated. Currency defaults to INR.

```bash
# Create order (automatically triggers notification)
# Note: customer is auto-assigned from authenticated user, tracking_number is auto-generated
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "ORD-001",
    "total_amount": "149.99",
    "currency": "INR",
    "shipping_address": "123 Main St, Mumbai, Maharashtra 400001",
    "shipping_method": "standard",
    "status": "pending",
    "notes": "Urgent delivery required"
  }'

# 🔒 ADMIN ONLY: Update order status (triggers status change notification)
curl -X PUT http://localhost:8000/api/v1/orders/ORDER_ID/status/ \
  -H "Authorization: Token ADMIN_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "confirmed"
  }'

# 🔒 ADMIN ONLY: Update entire order
curl -X PUT http://localhost:8000/api/v1/orders/ORDER_ID/ \
  -H "Authorization: Token ADMIN_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "shipped",
    "tracking_number": "TRK123456789",
    "notes": "Package shipped via express delivery"
  }'

# 🔒 ADMIN ONLY: Partial order update
curl -X PATCH http://localhost:8000/api/v1/orders/ORDER_ID/ \
  -H "Authorization: Token ADMIN_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "delivered"
  }'

# List all orders (available to all authenticated users)
curl -X GET http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# Get specific order (available to all authenticated users)
curl -X GET http://localhost:8000/api/v1/orders/ORDER_ID/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# 🔒 ADMIN ONLY: Delete order
curl -X DELETE http://localhost:8000/api/v1/orders/ORDER_ID/ \
  -H "Authorization: Token ADMIN_TOKEN_HERE"
```

### 5. MANUAL NOTIFICATION SYSTEM
```bash
# Send single notification
curl -X POST http://localhost:8000/api/v1/notifications/send/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Demo Notification",
    "message": "This is a test notification!",
    "recipient_type": "email",
    "recipient": "demo@example.com",
    "priority": "high"
  }'

# Send bulk notifications
curl -X POST http://localhost:8000/api/v1/notifications/bulk/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "notifications": [
      {
        "title": "Bulk Notification 1",
        "message": "First bulk message",
        "recipient_type": "email",
        "recipient": "user1@example.com"
      },
      {
        "title": "Bulk Notification 2",
        "message": "Second bulk message",
        "recipient_type": "telegram",
        "recipient": "123456789"
      }
    ]
  }'

# Get notification history
curl -X GET http://localhost:8000/api/v1/notifications/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# Get notification statistics
curl -X GET http://localhost:8000/api/v1/notifications/stats/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# Check specific notification status
curl -X GET http://localhost:8000/api/v1/notifications/NOTIFICATION_ID/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### 6. CUSTOMER NOTIFICATION PREFERENCES
```bash
# Get customer notification preferences
curl -X GET http://localhost:8000/api/v1/customers/CUSTOMER_ID/preferences/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# Update notification preferences
curl -X PATCH http://localhost:8000/api/v1/customers/CUSTOMER_ID/preferences/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "email_enabled": true,
    "telegram_enabled": false,
    "order_updates": true,
    "promotional": false
  }'
```

### 7. MONITORING & ANALYTICS
```bash
# System health check
curl -X GET http://localhost:8000/api/v1/health/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# Redis health check
curl -X GET http://localhost:8000/health/redis/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# Celery health check
curl -X GET http://localhost:8000/health/celery/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

---

## 🎬 DEMO VIDEO STRUCTURE

### Opening (30 seconds)
1. **Introduction**
   - Welcome to Django Notification System
   - Brief overview of capabilities
   - Architecture highlights

### Authentication Demo (1 minute)
2. **User Registration & Authentication**
   - Show user registration API
   - Token generation
   - Token validation

### Core Functionality (2 minutes)
3. **Customer Management**
   - Create customer
   - Update customer details
   - Show customer list

4. **Order Processing**
   - Create order (show automatic notification trigger)
   - Update order status (show status notification)
   - Display order history

### Notification System (1.5 minutes)
5. **Manual Notifications**
   - Send single notification
   - Send bulk notifications
   - Show delivery status

6. **Background Processing**
   - Show Celery worker logs
   - Demonstrate async processing

### Advanced Features (1 minute)
7. **Real-time Features**
   - WebSocket connection (if implemented)
   - Live status updates

8. **Monitoring & Health**
   - System health checks
   - Performance metrics

### Conclusion (30 seconds)
9. **Wrap-up**
   - Summary of features
   - Production readiness
   - Documentation links

---

## � SECURITY NOTES

### Admin Access Requirements
- **Admin Operations**: Order updates, deletions, and status changes require admin privileges
- **Admin Users**: Staff users (`is_staff=True`) or username `krushnappan`
- **Regular Users**: Can create, view orders but cannot modify them

### Token Types Required
- **USER_TOKEN**: For general operations (create orders, view data)
- **ADMIN_TOKEN**: For restricted operations (update/delete orders, status changes)

### Access Control Matrix
| Operation | User Access | Admin Required |
|-----------|-------------|----------------|
| Create Order | ✅ Yes | ❌ No |
| View Orders | ✅ Yes | ❌ No |
| Update Order | ❌ No | ✅ **Required** |
| Delete Order | ❌ No | ✅ **Required** |
| Update Status | ❌ No | ✅ **Required** |

---

## �🛠️ DEMO PREPARATION COMMANDS

### Start All Services
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Workers
celery -A config worker --loglevel=info --pool=solo

# Terminal 3: Django Server
python manage.py runserver 0.0.0.0:8000
```

### Quick Test Script
```bash
# Run the complete demo script
python demo_script.py

# Or run with custom URL
python demo_script.py http://your-server:8000
```

### Verify Setup
```bash
# Check Redis
redis-cli ping

# Check Django
curl http://localhost:8000/api/v1/health/

# Check API Docs
open http://localhost:8000/api/docs/
```

---

## 📱 DEMO TALKING POINTS

### Key Messages to Highlight:
1. **Enterprise Architecture** - Microservice design, scalable components
2. **Real-time Processing** - Async tasks, immediate notifications
3. **Multi-channel Support** - Email, Telegram, extensible for more
4. **Production Ready** - Docker, monitoring, error handling
5. **Developer Friendly** - API docs, comprehensive testing
6. **Security First** - Token auth, input validation, secure defaults

### Technical Depth to Show:
- Background task processing with Celery
- Redis caching and message queuing
- Automatic notification triggers on order events
- Error handling and retry mechanisms
- Health monitoring and metrics
- API documentation and testing tools

This flow provides a comprehensive demonstration of your Django Notification System's capabilities!
