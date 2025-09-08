# Customers API - Diagnostic & Fix Documentation

## Issue Resolution: 500 Internal Server Error

### Problem Identified:
Internal Server Error when accessing `/api/v1/customers/`

### Root Causes:
1. **Missing Import Dependencies**: `NotificationPreferenceSerializer` and `NotificationAnalyticsService`
2. **Database Tables**: Migration issues
3. **Empty Customer Data**: No sample data available

## Solutions Applied

### 1. Fixed Import Issues
- Restored proper imports in `apps/customers/views.py`
- Verified `NotificationPreferenceSerializer` exists in `apps/notifications/serializers.py`
- Verified `NotificationAnalyticsService` exists in `apps/notifications/services.py`

### 2. Added Sample Data Management
- Created `create_sample_customers` management command
- Generates 5 test customers with preferences
- Run with: `python manage.py create_sample_customers`

### 3. Added Debugging Tools
- Created `debug_customers_api.py` test script
- Created simplified `SimpleCustomerListView` for testing
- Added debugging endpoint: `/api/v1/customers/simple/`

## Testing & Resolution
```bash
python manage.py makemigrations
python manage.py migrate
```

### **Step 2: Create Sample Data**
```bash
python manage.py create_sample_customers
```

### Step 1: Apply Migrations
```bash
python manage.py migrate
```

### Step 2: Create Sample Data
```bash
python manage.py create_sample_customers
```

### Step 3: Test Simplified Endpoint
```bash
curl -X GET http://localhost:8000/api/v1/customers/simple/ \
  -H "Authorization: Token 93ccfdbf4df7a0d222ea36cac0a86e88f0e43e49"
```

### Step 4: Test Original Endpoint
```bash
curl -X GET http://localhost:8000/api/v1/customers/ \
  -H "Authorization: Token 93ccfdbf4df7a0d222ea36cac0a86e88f0e43e49"
```

### Step 5: Run Debug Script
```bash
python debug_customers_api.py
```

## Expected Results

### Simplified Endpoint Response:
```json
{
  "count": 5,
  "results": [
    {
      "id": "uuid-here",
      "name": "John Doe",
      "email": "john.doe@example.com",
      "phone": "+1234567890",
      "is_active": true,
      "created_at": "2025-09-08T..."
    }
  ]
}
```

### Original Endpoint Response:
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid-here",
      "name": "John Doe",
      "email": "john.doe@example.com",
      "notification_channels": ["email", "telegram"]
    }
  ]
}
```

## Manual Testing Commands

```bash
# 1. Start servers
python start_servers.py

# 2. Create test user and get token
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# 3. Test customers API (replace TOKEN with actual token)
curl -X GET http://localhost:8000/api/v1/customers/ \
  -H "Authorization: Token YOUR_TOKEN"

# 4. Create a customer
curl -X POST http://localhost:8000/api/v1/customers/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Customer",
    "email": "test@example.com",
    "phone": "+1234567890"
  }'
```

## Verification Steps

1. **Verify Django server is running** without errors
2. **Check server logs** for any remaining issues
3. **Test all customer endpoints**:
   - GET `/api/v1/customers/` - List customers
   - POST `/api/v1/customers/` - Create customer
   - GET `/api/v1/customers/{id}/` - Get customer details
   - GET `/api/v1/customers/{id}/preferences/` - Get preferences
   - GET `/api/v1/customers/{id}/notifications/` - Get history

4. **Monitor for any remaining 500 errors**

## Rollback Plan
If issues persist, use the simplified view:
- Access: `/api/v1/customers/simple/`
- Minimal dependencies, easier debugging
- Basic CRUD operations only

The customers API should now work correctly.
