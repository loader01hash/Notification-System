# ASGI Architecture - Django Notification System

## ASGI Configuration Overview

The Django Notification System has been enhanced with ASGI support for real-time WebSocket communications alongside the traditional HTTP API.

## Architecture Components

### ASGI Application Structure
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HTTP Client   │    │  WebSocket      │    │   ASGI App      │
│   (REST API)    │◄──►│   Client        │◄──►│   (Django)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Channel Layers  │    │ WebSocket       │
                       │    (Redis)      │    │  Consumers      │
                       └─────────────────┘    └─────────────────┘
```

### Channel Layer Configuration
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
            "capacity": 1500,
            "expiry": 60,
        },
    },
}
```

## WebSocket Features

### Real-time Notification Broadcasting
- General notification broadcasts to all connected clients
- User-specific notification channels for targeted messaging
- Real-time status updates for order processing
- Health check ping/pong mechanisms

### WebSocket Consumers
1. **General Notification Consumer**
   - Path: `/ws/notifications/`
   - Purpose: Broadcast system-wide notifications

2. **User-specific Consumer**
   - Path: `/ws/notifications/{user_id}/`
   - Purpose: Targeted user notifications

3. **Health Check Consumer**
   - Path: `/ws/health/`
   - Purpose: System health monitoring

## Implementation Details

### ASGI Configuration Fix
The system addresses Django's deprecated `is_ajax()` method:

```python
# Fixed Debug Toolbar Configuration
'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG and request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest'
```

### WebSocket URL Routing
```python
websocket_urlpatterns = [
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/notifications/(?P<user_id>\w+)/$', UserNotificationConsumer.as_asgi()),
    re_path(r'ws/health/$', HealthConsumer.as_asgi()),
]
```

### Consumer Implementation
```python
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)
    
    async def receive(self, text_data):
        # Handle incoming WebSocket messages
        pass
    
    async def notification_message(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps(event['message']))
```

## Integration with Notification System

### Celery Task Integration
```python
@shared_task(bind=True)
def send_notification_task(self, notification_data):
    # Process notification
    result = process_notification(notification_data)
    
    # Broadcast via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "notifications",
        {
            "type": "notification_message",
            "message": {
                "notification_id": notification_data['id'],
                "status": result['status'],
                "timestamp": timezone.now().isoformat()
            }
        }
    )
    return result
```

## Benefits of ASGI Implementation

1. **Real-time Updates**: Immediate notification delivery status updates
2. **Bidirectional Communication**: Client-server interaction beyond HTTP request/response
3. **Scalable Architecture**: Asynchronous handling of multiple connections
4. **Enhanced User Experience**: Live status updates and instant feedback
5. **System Monitoring**: Real-time health checks and system status

## Deployment Considerations

### Production Setup
- Use production-grade ASGI server (Daphne, Uvicorn)
- Configure Redis cluster for channel layer scaling
- Implement proper WebSocket authentication
- Set up monitoring for WebSocket connections
- Configure load balancing for WebSocket connections

### Security Considerations
- Implement WebSocket authentication middleware
- Validate and sanitize all WebSocket messages
- Rate limiting for WebSocket connections
- CORS configuration for WebSocket origins
- SSL/TLS for secure WebSocket connections (WSS)

## Testing WebSocket Functionality

### Connection Test
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/notifications/');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Notification received:', data);
};
```

### Health Check Test
```javascript
const healthWs = new WebSocket('ws://localhost:8000/ws/health/');
healthWs.onopen = function() {
    healthWs.send(JSON.stringify({type: 'ping'}));
};
```

This ASGI enhancement provides a robust foundation for real-time features while maintaining the REST API functionality for standard operations.
