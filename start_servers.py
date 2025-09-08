"""
Startup script for Django Notification System
Starts both Django server and Celery worker.
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def start_servers():
    """Start Django and Celery servers."""
    
    print("🚀 DJANGO NOTIFICATION SYSTEM STARTUP")
    print("=" * 45)
    
    # Get the Python executable path
    venv_path = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
    python_exe = str(venv_path) if venv_path.exists() else "python"
    
    print(f"📍 Using Python: {python_exe}")
    print(f"📁 Working Directory: {os.getcwd()}")
    
    # Check if manage.py exists
    if not os.path.exists("manage.py"):
        print("❌ Error: manage.py not found. Make sure you're in the project directory.")
        return
    
    print("\n🔴 IMPORTANT: Make sure Redis is running on localhost:6379")
    print("   - Install Redis or use Docker: docker run -d -p 6379:6379 redis:alpine")
    print("   - Or use WSL with Redis installed")
    
    try:
        print("\n🌐 Starting Django Development Server...")
        django_process = subprocess.Popen([
            python_exe, "manage.py", "runserver", "0.0.0.0:8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("   ✅ Django server starting...")
        time.sleep(3)  # Give Django time to start
        
        print("\n🐝 Starting Celery Worker...")
        celery_process = subprocess.Popen([
            python_exe, "-m", "celery", "-A", "config", "worker", 
            "--loglevel=info", "--pool=solo"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("   ✅ Celery worker starting...")
        time.sleep(2)
        
        print("\n🎉 SERVERS STARTED SUCCESSFULLY!")
        print("=" * 45)
        print("📊 Service Status:")
        print("   🌐 Django Server:    http://localhost:8000")
        print("   📚 API Docs:         http://localhost:8000/api/docs/")
        print("   🔐 Quick Token:      http://localhost:8000/api/v1/auth/quick-token/")
        print("   🔔 Notifications:    http://localhost:8000/api/v1/notifications/")
        print("   🐝 Celery Worker:    Running in background")
        
        print("\n🧪 Test Commands:")
        print("   python test_auth.py")
        print("   python test_swagger_fix.py")
        print("   python test_quick_token.py")
        
        print("\n💡 Press Ctrl+C to stop both servers...")
        
        # Keep the script running and monitor processes
        try:
            while True:
                # Check if processes are still running
                django_poll = django_process.poll()
                celery_poll = celery_process.poll()
                
                if django_poll is not None:
                    print(f"\n⚠️  Django server stopped (exit code: {django_poll})")
                    break
                    
                if celery_poll is not None:
                    print(f"\n⚠️  Celery worker stopped (exit code: {celery_poll})")
                    break
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping servers...")
            django_process.terminate()
            celery_process.terminate()
            
            # Wait for graceful shutdown
            try:
                django_process.wait(timeout=5)
                celery_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("   Force killing processes...")
                django_process.kill()
                celery_process.kill()
            
            print("   ✅ Servers stopped.")
            
    except FileNotFoundError:
        print(f"❌ Error: Python executable not found at {python_exe}")
        print("   Make sure the virtual environment is set up correctly.")
    except Exception as e:
        print(f"❌ Error starting servers: {e}")

if __name__ == "__main__":
    start_servers()
