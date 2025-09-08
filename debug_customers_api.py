"""
Test script to debug the customers API 500 error.
"""
import requests
import json
import traceback

def test_customers_api():
    """Test the customers API endpoint."""
    
    print("🔍 DEBUGGING CUSTOMERS API 500 ERROR")
    print("=" * 45)
    
    BASE_URL = "http://localhost:8000/api/v1"
    
    # First, let's get a token
    print("\n1️⃣  Getting authentication token...")
    try:
        auth_response = requests.post(f"{BASE_URL}/auth/register/", json={
            "username": "test_customer_user",
            "password": "test_password_123",
            "email": "testcustomer@example.com"
        }, timeout=10)
        
        if auth_response.status_code == 201:
            token = auth_response.json().get('token')
            print(f"   ✅ Got token: {token[:20]}...")
        else:
            # Try to login instead
            login_response = requests.post(f"{BASE_URL}/auth/token/", json={
                "username": "test_customer_user",
                "password": "test_password_123"
            }, timeout=10)
            
            if login_response.status_code == 200:
                token = login_response.json().get('token')
                print(f"   ✅ Logged in, got token: {token[:20]}...")
            else:
                print(f"   ❌ Auth failed: {login_response.status_code} - {login_response.text}")
                return
                
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to Django server")
        print("   💡 Start server with: python manage.py runserver 0.0.0.0:8000")
        return
    except Exception as e:
        print(f"   ❌ Auth error: {e}")
        return
    
    # Set up headers
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    print("\n2️⃣  Testing customers API...")
    
    # Test GET /customers/
    try:
        print("   Testing GET /api/v1/customers/")
        response = requests.get(f"{BASE_URL}/customers/", headers=headers, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Found {len(data.get('results', data))} customers")
            print(f"   Response: {json.dumps(data, indent=2)[:500]}...")
        else:
            print(f"   ❌ Error Response:")
            print(f"   {response.text}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        traceback.print_exc()
    
    print("\n3️⃣  Testing individual endpoints...")
    
    # Test other endpoints
    endpoints = [
        ("GET", "/api/v1/", "API Gateway"),
        ("GET", "/api/v1/notifications/", "Notifications"),
        ("GET", "/api/v1/orders/", "Orders"),
    ]
    
    for method, endpoint, name in endpoints:
        try:
            print(f"   Testing {method} {endpoint} ({name})")
            response = requests.get(f"{BASE_URL.replace('/api/v1', '')}{endpoint}", headers=headers, timeout=5)
            print(f"      Status: {response.status_code}")
        except Exception as e:
            print(f"      Error: {e}")
    
    print("\n💡 Debugging tips:")
    print("   1. Check Django server logs for detailed error messages")
    print("   2. Verify all migrations are applied: python manage.py migrate")
    print("   3. Check if sample data exists: python manage.py create_sample_customers")
    print("   4. Test with Django admin: http://localhost:8000/admin/")

if __name__ == "__main__":
    test_customers_api()
