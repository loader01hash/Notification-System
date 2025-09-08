"""
WebSocket consumers for real-time notifications.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for general notification broadcasts.
    """
    
    async def connect(self):
        """Accept WebSocket connection and join notification group."""
        self.room_group_name = 'notifications_broadcast'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected: {self.channel_name}")
    
    async def disconnect(self, close_code):
        """Leave room group on disconnect."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected: {self.channel_name}")
    
    async def receive(self, text_data):
        """Handle messages from WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'message')
            message = text_data_json.get('message', '')
            
            # Echo message back to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'notification_message',
                    'message': message,
                    'message_type': message_type,
                }
            )
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
    
    async def notification_message(self, event):
        """Send notification message to WebSocket."""
        message = event['message']
        message_type = event.get('message_type', 'info')
        
        await self.send(text_data=json.dumps({
            'type': message_type,
            'message': message,
            'timestamp': str(timezone.now()) if 'timezone' in globals() else None,
        }))


class UserNotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for user-specific notifications.
    """
    
    async def connect(self):
        """Accept WebSocket connection for specific user."""
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'user_notifications_{self.user_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User WebSocket connected: {self.channel_name} for user {self.user_id}")
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': f'Connected to notifications for user {self.user_id}',
        }))
    
    async def disconnect(self, close_code):
        """Leave room group on disconnect."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"User WebSocket disconnected: {self.channel_name}")
    
    async def receive(self, text_data):
        """Handle messages from WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'message')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'message': 'pong',
                }))
            elif message_type == 'status':
                # Get user notification status
                status = await self.get_user_notification_status()
                await self.send(text_data=json.dumps({
                    'type': 'status',
                    'data': status,
                }))
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
    
    async def user_notification(self, event):
        """Send user-specific notification to WebSocket."""
        notification_data = event['notification']
        
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': notification_data,
        }))
    
    @database_sync_to_async
    def get_user_notification_status(self):
        """Get notification status for user."""
        from .models import Notification
        
        try:
            # Get recent notifications for user
            recent_notifications = Notification.objects.filter(
                customer_id=self.user_id
            ).order_by('-created_at')[:10]
            
            return {
                'user_id': self.user_id,
                'recent_count': recent_notifications.count(),
                'notifications': [
                    {
                        'id': str(notification.id),
                        'subject': notification.subject,
                        'status': notification.status,
                        'created_at': notification.created_at.isoformat(),
                    }
                    for notification in recent_notifications
                ]
            }
        except Exception as e:
            logger.error(f"Error getting user notification status: {e}")
            return {'error': 'Failed to get notification status'}


# Helper function to send real-time notifications
async def send_realtime_notification(user_id, notification_data):
    """
    Send real-time notification to specific user via WebSocket.
    """
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    if channel_layer:
        await channel_layer.group_send(
            f'user_notifications_{user_id}',
            {
                'type': 'user_notification',
                'notification': notification_data,
            }
        )


# Helper function to broadcast general notifications
async def broadcast_notification(message, message_type='info'):
    """
    Broadcast notification to all connected clients.
    """
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    if channel_layer:
        await channel_layer.group_send(
            'notifications_broadcast',
            {
                'type': 'notification_message',
                'message': message,
                'message_type': message_type,
            }
        )
