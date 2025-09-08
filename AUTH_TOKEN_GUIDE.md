# Authentication Token Guide

## Authentication System Overview

The Django notification system includes a complete authentication system. Here are the methods to obtain and use tokens:

## Getting Authentication Tokens

### Method 1: Create User & Get Token (Recommended)
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "password": "secure_password123",
    "email": "demo@example.com",
    "first_name": "Demo",
    "last_name": "User"
  }'
```

**Response:**
```json
{
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
  "user_id": 1,
  "username": "demo_user",
  "message": "User created successfully"
}
### Method 2: Login with Existing User
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "password": "secure_password123"
  }'
```

## Using Your Token

Once you have a token, include it in the Authorization header:

```bash
curl -X GET http://localhost:8000/api/v1/notifications/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
```

## Authentication Endpoints

### 1. Register New User
- **URL**: `POST /api/v1/auth/register/`
- **Purpose**: Create new user account and get token
- **Auth Required**: No
- **Body**:
```json
{
  "username": "your_username",
  "password": "your_password",
  "email": "email@example.com",          // Optional
  "first_name": "First",                  // Optional
  "last_name": "Last"                     // Optional
}
```

### 2. Get Token (Login)
- **URL**: `POST /api/v1/auth/token/`
- **Purpose**: Get token for existing user
- **Auth Required**: No
- **Body**:
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

### 3. Check Token Status
- **URL**: `GET /api/v1/auth/token/check/`
- **Purpose**: Verify token validity and get user info
- **Auth Required**: Yes (Token)
- **Headers**: `Authorization: Token YOUR_TOKEN`

### 4. Refresh Token
- **URL**: `POST /api/v1/auth/token/refresh/`
- **Purpose**: Generate new token (invalidates old one)
- **Auth Required**: Yes (Token)
- **Headers**: `Authorization: Token YOUR_TOKEN`

### 5. Revoke Token (Logout)
- **URL**: `POST /api/v1/auth/token/revoke/`
- **Purpose**: Delete token (logout)
- **Auth Required**: Yes (Token)
- **Headers**: `Authorization: Token YOUR_TOKEN`

### 6. Quick Token (Simple)
- **URL**: `POST /api/v1/auth/quick-token/`
- **Purpose**: Simple token endpoint
- **Auth Required**: No

### 7. Quick Check (Simple)
- **URL**: `GET /api/v1/auth/quick-check/`
- **Purpose**: Simple token validation
- **Auth Required**: Yes (Token)

## Setup Commands

Before using authentication, run these commands:

```bash
# Make sure you're in the project directory
cd c:\Users\10710485\Desktop\python\notification

# Apply database migrations for token tables
python manage.py makemigrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser

# Start the server
python -m uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --reload
```

## Complete Test Script

Here's a complete test script to try all authentication features:

```bash
# 1. Register a new user
echo "=== Creating User ==="
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123", "email": "test@example.com"}'

echo -e "\n\n=== Getting Token ==="
# 2. Get token (login)
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}')

echo $TOKEN_RESPONSE

# Extract token (on Windows, you might need to do this manually)
# TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

echo -e "\n\n=== Checking Token Status ==="
# 3. Check token status (replace YOUR_TOKEN with actual token)
curl -X GET http://localhost:8000/api/v1/auth/token/check/ \
  -H "Authorization: Token YOUR_TOKEN"

echo -e "\n\n=== Testing API with Token ==="
# 4. Use token to access protected endpoint
curl -X GET http://localhost:8000/api/v1/notifications/ \
  -H "Authorization: Token YOUR_TOKEN"
```

## Python Script Example

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 1. Register user
register_data = {
    "username": "api_user",
    "password": "secure_pass123",
    "email": "api@example.com"
}

response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
result = response.json()
print("Registration:", result)

# Get the token
token = result.get('token')
headers = {'Authorization': f'Token {token}'}

# 2. Check token status
response = requests.get(f"{BASE_URL}/auth/token/check/", headers=headers)
print("Token Status:", response.json())

# 3. Use token to access notifications
response = requests.get(f"{BASE_URL}/notifications/", headers=headers)
print("Notifications:", response.json())

# 4. Create a notification
notification_data = {
    "title": "Test Notification",
    "message": "This is a test notification",
    "recipient_type": "email",
    "recipient": "test@example.com"
}

response = requests.post(f"{BASE_URL}/notifications/send/", 
                        json=notification_data, headers=headers)
print("Send Notification:", response.json())
```

## Security Notes

1. **Token Storage**: Store tokens securely (environment variables, secure storage)
2. **Token Expiration**: Tokens don't expire by default, use refresh endpoint regularly
3. **HTTPS**: Use HTTPS in production
4. **Token Rotation**: Refresh tokens periodically for security

## API Documentation

Access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

The authentication endpoints will be documented there with try-it-now functionality.

## Common Use Cases

### Frontend Login Flow:
1. User enters credentials → `POST /auth/token/`
2. Store token in localStorage/sessionStorage
3. Include token in all API requests
4. Check token validity → `GET /auth/token/check/`
5. Refresh token periodically → `POST /auth/token/refresh/`
6. Logout → `POST /auth/token/revoke/`

### API Integration:
1. Register service account → `POST /auth/register/`
2. Get token → `POST /auth/token/`
3. Use token for all API calls
4. Monitor token status → `GET /auth/token/check/`

Your authentication system is now fully functional and ready for production use.
