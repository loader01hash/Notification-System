@echo off
echo 🔐 AUTHENTICATION TOKEN COMMANDS
echo ================================

echo.
echo 1️⃣  REGISTER NEW USER:
echo curl -X POST http://localhost:8000/api/v1/auth/register/ -H "Content-Type: application/json" -d "{\"username\": \"demo_user\", \"password\": \"secure_password123\", \"email\": \"demo@example.com\"}"

echo.
echo 2️⃣  GET TOKEN (LOGIN):
echo curl -X POST http://localhost:8000/api/v1/auth/token/ -H "Content-Type: application/json" -d "{\"username\": \"demo_user\", \"password\": \"secure_password123\"}"

echo.
echo 3️⃣  CHECK TOKEN STATUS:
echo curl -X GET http://localhost:8000/api/v1/auth/token/check/ -H "Authorization: Token YOUR_TOKEN_HERE"

echo.
echo 4️⃣  USE TOKEN TO ACCESS NOTIFICATIONS:
echo curl -X GET http://localhost:8000/api/v1/notifications/ -H "Authorization: Token YOUR_TOKEN_HERE"

echo.
echo 5️⃣  REFRESH TOKEN:
echo curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ -H "Authorization: Token YOUR_TOKEN_HERE"

echo.
echo 6️⃣  REVOKE TOKEN (LOGOUT):
echo curl -X POST http://localhost:8000/api/v1/auth/token/revoke/ -H "Authorization: Token YOUR_TOKEN_HERE"

echo.
echo 🌐 ACCESS POINTS:
echo   Health Check: http://localhost:8000/health/
echo   API Docs:     http://localhost:8000/api/docs/
echo   ReDoc:        http://localhost:8000/api/redoc/

echo.
echo 💡 STEPS TO GET YOUR TOKEN:
echo   1. Start server: python manage.py runserver
echo   2. Register user (command #1 above)
echo   3. Copy the token from response
echo   4. Replace YOUR_TOKEN_HERE with actual token
echo   5. Use token in all authenticated requests

pause
