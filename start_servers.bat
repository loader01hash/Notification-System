@echo off
echo 🚀 DJANGO NOTIFICATION SYSTEM - STARTUP SCRIPT
echo ================================================

echo.
echo 📋 Starting Services...
echo ========================

REM Check if Redis is running (optional check)
echo 🔴 Note: Make sure Redis server is running on localhost:6379
echo    - Download Redis for Windows or use WSL
echo    - Or use Docker: docker run -d -p 6379:6379 redis:alpine
echo.

REM Set the Python executable path
set PYTHON_PATH=C:/Users/10710485/Desktop/python/notification/.venv/Scripts/python.exe

echo 🔧 Starting Django Development Server...
start "Django Server" cmd /k "%PYTHON_PATH% manage.py runserver 0.0.0.0:8000"

echo.
echo ⏱️  Waiting 3 seconds for Django to start...
timeout /t 3 /nobreak >nul

echo.
echo 🐝 Starting Celery Worker...
start "Celery Worker" cmd /k "%PYTHON_PATH% -m celery -A config worker --loglevel=info --pool=solo"

echo.
echo ✅ Both servers are starting!
echo.
echo 📊 Service Status:
echo ==================
echo 🌐 Django Server:    http://localhost:8000
echo 📚 API Docs:         http://localhost:8000/api/docs/
echo 🔐 Auth Endpoints:   http://localhost:8000/api/v1/auth/
echo 🔔 Notifications:    http://localhost:8000/api/v1/notifications/
echo 🐝 Celery Worker:    Running in background
echo.
echo 💡 Both terminal windows will stay open for monitoring.
echo    Close them when you want to stop the services.
echo.
pause
