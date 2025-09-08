# Celery Server Status

## Current Server Status

### Django Development Server
- **Status**: Ready to start
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs/
- **Command**: `python manage.py runserver 0.0.0.0:8000`

### Celery Worker Server
- **Status**: Running
- **Worker Name**: celery@N3NXCV15K63812F
- **Version**: 5.5.3
- **Pool**: solo (Windows compatible)
- **Concurrency**: 8 workers
- **Transport**: redis://localhost:6379/1
- **Results**: redis://localhost:6379/2

### Available Celery Tasks
All notification tasks registered:
- `apps.notifications.tasks.send_notification_task`
- `apps.notifications.tasks.send_bulk_notifications_task`
- `apps.notifications.tasks.send_order_update_notification`
- `apps.notifications.tasks.process_scheduled_notifications`
- `apps.notifications.tasks.retry_failed_notifications`
- `apps.notifications.tasks.cleanup_old_notifications`
- `config.celery.debug_task`

### Notification Channels Loaded
All channels registered successfully:
- Telegram Channel
- Email Channel
- Email Channel (SMTP)
- Telegram Channel (Bot API)

## Quick Start Options

### Option 1: Use Batch Script (Recommended)
```bash
start_servers.bat
```
- Starts both Django and Celery in separate windows
- Easy monitoring and management

### Option 2: Use Python Script
```bash
python start_servers.py
```
- Starts both servers with unified monitoring
- Press Ctrl+C to stop both

### Option 3: Manual Start
```bash
# Terminal 1: Django Server
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Celery Worker (already running!)
celery -A config worker --loglevel=info --pool=solo
```

## Test Your Setup

### Check Server Status
```bash
python check_status.py
```

### Test Authentication
```bash
python test_auth.py
```

### Test Swagger Documentation
```bash
python test_swagger_fix.py
```

### Test Notifications
```bash
# Create a notification via API
curl -X POST http://localhost:8000/api/v1/notifications/send/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Notification",
    "message": "Testing Celery background processing!",
    "recipient_type": "email",
    "recipient": "test@example.com"
  }'
```

## Requirements

### Redis Server
**IMPORTANT**: Make sure Redis is running on localhost:6379

**Install Options:**
1. **Docker (Recommended)**:
   ```bash
   docker run -d -p 6379:6379 --name redis redis:alpine
   ```

2. **Windows Redis**:
   - Download from: https://github.com/microsoftarchive/redis/releases
   - Or use WSL with Redis

3. **Check Redis Status**:
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

## Monitoring

### Celery Worker Logs
The Celery worker is running and will show:
- Task executions
- Error messages
- Performance metrics
- Connection status

### Django Server Logs
Start Django to see:
- HTTP requests
- API calls
- Authentication attempts
- Error messages

## System Status

**Celery Worker**: Running and ready to process tasks
**Task Registration**: All notification tasks loaded
**Channel Registration**: All notification channels available
**Redis Connection**: Connected to localhost:6379
**Authentication System**: Ready for token-based auth
**API Documentation**: Swagger UI available
**WebSocket Support**: ASGI configuration ready

## Next Steps

1. **Start Django server** using one of the options above
2. **Test the complete system** with the provided test scripts
3. **Create notifications** via API and watch them process in Celery
4. **Monitor both servers** for any issues

Your Django Notification System with Celery is now fully operational.
