"""
Check the status of Django and Celery servers.
"""
import requests
import time
import subprocess
import sys

def check_server_status():
    """Check if Django and Celery are running properly."""
    
    print("🔍 SERVER STATUS CHECK")
    print("=" * 30)
    
    # Check Django server
    print("\n1️⃣  Django Server Check:")
    try:
        response = requests.get("http://localhost:8000/api/v1/health/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Django server is running")
            print(f"   📊 Response time: {response.elapsed.total_seconds():.2f}s")
        else:
            print(f"   ⚠️  Django server responding but status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Django server is not running")
        print("   💡 Start with: python manage.py runserver 0.0.0.0:8000")
    except Exception as e:
        print(f"   ❌ Error checking Django: {e}")
    
    # Check API endpoints
    print("\n2️⃣  API Endpoints Check:")
    endpoints = [
        ("/api/v1/", "API Gateway"),
        ("/api/docs/", "Swagger UI"),
        ("/api/v1/auth/quick-token/", "Authentication"),
        ("/api/v1/notifications/", "Notifications")
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=3)
            status = "✅" if response.status_code in [200, 401, 403] else "⚠️"
            print(f"   {status} {name}: {response.status_code}")
        except:
            print(f"   ❌ {name}: Not accessible")
    
    # Check Redis connection
    print("\n3️⃣  Redis Connection Check:")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("   ✅ Redis is running and accessible")
    except ImportError:
        print("   ⚠️  Redis package not installed (pip install redis)")
    except Exception as e:
        print("   ❌ Redis is not running or not accessible")
        print("   💡 Start Redis server or use Docker: docker run -d -p 6379:6379 redis:alpine")
    
    # Check Celery tasks
    print("\n4️⃣  Celery Task Check:")
    try:
        # Try to import Celery app
        from config.celery import app as celery_app
        
        # Check active workers
        stats = celery_app.control.inspect().stats()
        if stats:
            worker_count = len(stats)
            print(f"   ✅ Celery workers active: {worker_count}")
            for worker_name in stats.keys():
                print(f"      - {worker_name}")
        else:
            print("   ❌ No Celery workers found")
            print("   💡 Start with: celery -A config worker --loglevel=info --pool=solo")
            
    except Exception as e:
        print(f"   ❌ Error checking Celery: {e}")
    
    # Test authentication
    print("\n5️⃣  Authentication Test:")
    try:
        # Try to register a test user
        test_data = {
            "username": "status_test_user",
            "password": "test_password_123"
        }
        
        response = requests.post("http://localhost:8000/api/v1/auth/quick-token/", 
                               json=test_data, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Authentication working")
            print(f"   🔑 Test token: {result.get('token', 'N/A')[:20]}...")
        elif response.status_code == 400:
            print("   ✅ Authentication endpoint responding (credentials needed)")
        else:
            print(f"   ⚠️  Authentication status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
    
    print("\n📋 SUMMARY:")
    print("   🌐 Django:  http://localhost:8000")
    print("   📚 Docs:    http://localhost:8000/api/docs/")
    print("   🔐 Auth:    http://localhost:8000/api/v1/auth/quick-token/")
    
    print("\n🛠️  If issues found:")
    print("   1. Start servers: python start_servers.py")
    print("   2. Or manually:")
    print("      - Django: python manage.py runserver 0.0.0.0:8000")
    print("      - Celery: celery -A config worker --loglevel=info --pool=solo")
    print("   3. Check Redis: Make sure Redis server is running")

if __name__ == "__main__":
    check_server_status()
