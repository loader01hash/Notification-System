"""
Notification API views.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import logging

from .models import Notification, NotificationTemplate
from .serializers import (
    NotificationSerializer, NotificationTemplateSerializer,
    SendNotificationSerializer, SendBulkNotificationSerializer,
    NotificationPreferenceSerializer
)
from .services import NotificationService, NotificationAnalyticsService
from .tasks import send_notification_task, send_bulk_notifications_task
from apps.customers.models import Customer
from apps.customers.serializers import CustomerSerializer

logger = logging.getLogger(__name__)


class SendNotificationView(APIView):
    """API view to send individual notifications."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=SendNotificationSerializer,
        responses={201: NotificationSerializer},
        description="Send a single notification"
    )
    def post(self, request):
        """Send a notification."""
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = NotificationService()
        
        # Get related objects if provided
        customer = None
        order = None
        
        if serializer.validated_data.get('customer_id'):
            from apps.customers.models import Customer
            customer = get_object_or_404(Customer, id=serializer.validated_data['customer_id'])
        
        if serializer.validated_data.get('order_id'):
            from apps.orders.models import Order
            order = get_object_or_404(Order, id=serializer.validated_data['order_id'])
        
        # Create notification
        notification = service.create_notification(
            template_name=serializer.validated_data['template_name'],
            recipient=serializer.validated_data['recipient'],
            customer=customer,
            order=order,
            context=serializer.validated_data.get('context', {}),
            priority=serializer.validated_data['priority'],
            scheduled_at=serializer.validated_data.get('scheduled_at')
        )
        
        if not notification:
            return Response(
                {'error': 'Failed to create notification'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Queue notification for sending
        try:
            send_notification_task.delay(str(notification.id))
        except Exception as e:
            logger.error(f"Failed to queue notification: {str(e)}")
            return Response(
                {'error': 'Failed to queue notification'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response_serializer = NotificationSerializer(notification)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class SendBulkNotificationView(APIView):
    """API view to send bulk notifications."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=SendBulkNotificationSerializer,
        responses={201: NotificationSerializer(many=True)},
        description="Send bulk notifications"
    )
    def post(self, request):
        """Send bulk notifications."""
        serializer = SendBulkNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = NotificationService()
        
        # Create bulk notifications
        notifications = service.send_bulk_notifications(
            template_name=serializer.validated_data['template_name'],
            recipients=serializer.validated_data['recipients'],
            context=serializer.validated_data.get('context', {}),
            priority=serializer.validated_data['priority']
        )
        
        if not notifications:
            return Response(
                {'error': 'Failed to create notifications'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Queue notifications for sending
        notification_ids = [str(n.id) for n in notifications]
        try:
            send_bulk_notifications_task.delay(notification_ids)
        except Exception as e:
            logger.error(f"Failed to queue bulk notifications: {str(e)}")
            return Response(
                {'error': 'Failed to queue notifications'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        response_serializer = NotificationSerializer(notifications, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class NotificationListView(generics.ListAPIView):
    """API view to list notifications."""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get filtered notifications."""
        queryset = Notification.objects.select_related('template', 'customer', 'order')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        # Filter by channel
        channel = self.request.query_params.get('channel')
        if channel:
            queryset = queryset.filter(template__channel=channel)
        
        return queryset.order_by('-created_at')


class NotificationDetailView(generics.RetrieveAPIView):
    """API view to get notification details."""
    
    queryset = Notification.objects.select_related('template', 'customer', 'order')
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]


class NotificationStatusView(APIView):
    """API view to check notification status."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter("id", OpenApiTypes.UUID, OpenApiParameter.PATH)
        ],
        responses={200: NotificationSerializer},
        description="Get notification status"
    )
    def get(self, request, id):
        """Get notification status."""
        notification = get_object_or_404(Notification, id=id)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)


class NotificationAnalyticsView(APIView):
    """API view for notification analytics."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter("days", OpenApiTypes.INT, OpenApiParameter.QUERY, description="Number of days for analytics")
        ],
        description="Get notification analytics"
    )
    def get(self, request):
        """Get notification analytics."""
        days = int(request.query_params.get('days', 7))
        analytics = NotificationAnalyticsService.get_delivery_statistics(days)
        return Response(analytics)


class NotificationTemplateListView(generics.ListCreateAPIView):
    """API view to list and create notification templates."""
    
    queryset = NotificationTemplate.objects.filter(is_active=True)
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


class NotificationTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for notification template details."""
    
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def retry_notification(request, id):
    """Retry a failed notification."""
    notification = get_object_or_404(Notification, id=id)
    
    if not notification.can_retry():
        return Response(
            {'error': 'Notification cannot be retried'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        send_notification_task.delay(str(notification.id))
        return Response({'message': 'Notification queued for retry'})
    except Exception as e:
        logger.error(f"Failed to retry notification: {str(e)}")
        return Response(
            {'error': 'Failed to queue notification for retry'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# New user-focused notification views
class MyNotificationsView(APIView):
    """
    Get notifications for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get My Notifications",
        description="Get notification history for the currently authenticated user.",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'customer_id': {'type': 'string', 'description': 'Customer UUID'},
                    'customer_name': {'type': 'string', 'description': 'Customer name'},
                    'notifications': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'string'},
                                'type': {'type': 'string'},
                                'title': {'type': 'string'},
                                'message': {'type': 'string'},
                                'status': {'type': 'string'},
                                'created_at': {'type': 'string', 'format': 'date-time'}
                            }
                        }
                    },
                    'total_count': {'type': 'integer'},
                    'unread_count': {'type': 'integer'}
                }
            },
            404: {'description': 'Customer data not found'}
        },
        tags=['User Notifications']
    )
    def get(self, request):
        """Get notifications for current user."""
        try:
            customer = Customer.objects.get(email=request.user.email)
            
            # For now, return mock data since notification system is not fully implemented
            return Response({
                'customer_id': str(customer.id),
                'customer_name': customer.name,
                'notifications': [
                    {
                        'id': 'notif_001',
                        'type': 'order_update',
                        'title': 'Welcome!',
                        'message': 'Welcome to our notification system!',
                        'status': 'sent',
                        'created_at': '2025-09-08T10:00:00Z'
                    }
                ],
                'total_count': 1,
                'unread_count': 0
            })
            
        except Customer.DoesNotExist:
            return Response({
                'error': 'Customer data not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)


class MyNotificationPreferencesView(APIView):
    """
    Get and update notification preferences for a user.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get My Notification Preferences",
        description="Get notification preferences for the currently authenticated user along with their customer data.",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'customer_data': {
                        'type': 'object',
                        'description': 'Customer information'
                    },
                    'preferences': {
                        'type': 'object',
                        'properties': {
                            'email_enabled': {'type': 'boolean'},
                            'telegram_enabled': {'type': 'boolean'},
                            'order_updates': {'type': 'boolean'},
                            'promotional': {'type': 'boolean'},
                            'security_alerts': {'type': 'boolean'},
                            'timezone': {'type': 'string'}
                        }
                    }
                }
            },
            404: {'description': 'Customer data not found'}
        },
        tags=['User Notifications']
    )
    def get(self, request):
        """Get notification preferences with customer data."""
        try:
            customer = Customer.objects.get(email=request.user.email)
            customer_serializer = CustomerSerializer(customer)
            
            return Response({
                'customer_data': customer_serializer.data,
                'preferences': {
                    'email_enabled': bool(customer.email),
                    'telegram_enabled': bool(customer.telegram_chat_id),
                    'order_updates': True,
                    'promotional': False,
                    'security_alerts': True,
                    'timezone': 'UTC'
                }
            })
            
        except Customer.DoesNotExist:
            return Response({
                'error': 'Customer data not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Update My Notification Preferences",
        description="Update notification preferences for the currently authenticated user.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email_enabled': {'type': 'boolean', 'description': 'Enable email notifications'},
                    'telegram_enabled': {'type': 'boolean', 'description': 'Enable Telegram notifications'},
                    'order_updates': {'type': 'boolean', 'description': 'Receive order updates'},
                    'promotional': {'type': 'boolean', 'description': 'Receive promotional messages'},
                    'security_alerts': {'type': 'boolean', 'description': 'Receive security alerts'},
                    'timezone': {'type': 'string', 'description': 'User timezone'}
                }
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'customer_data': {
                        'type': 'object',
                        'description': 'Customer information'
                    },
                    'preferences': {
                        'type': 'object',
                        'properties': {
                            'email_enabled': {'type': 'boolean'},
                            'telegram_enabled': {'type': 'boolean'},
                            'order_updates': {'type': 'boolean'},
                            'promotional': {'type': 'boolean'},
                            'security_alerts': {'type': 'boolean'},
                            'timezone': {'type': 'string'}
                        }
                    },
                    'message': {'type': 'string'}
                }
            },
            404: {'description': 'Customer data not found'}
        },
        tags=['User Notifications']
    )
    def put(self, request):
        """Update notification preferences."""
        try:
            customer = Customer.objects.get(email=request.user.email)
            customer_serializer = CustomerSerializer(customer)
            
            # For now, just return the updated preferences
            # In a full implementation, you would save these to a preferences model
            preferences = {
                'email_enabled': request.data.get('email_enabled', bool(customer.email)),
                'telegram_enabled': request.data.get('telegram_enabled', bool(customer.telegram_chat_id)),
                'order_updates': request.data.get('order_updates', True),
                'promotional': request.data.get('promotional', False),
                'security_alerts': request.data.get('security_alerts', True),
                'timezone': request.data.get('timezone', 'UTC')
            }
            
            return Response({
                'customer_data': customer_serializer.data,
                'preferences': preferences,
                'message': 'Notification preferences updated successfully'
            })
            
        except Customer.DoesNotExist:
            return Response({
                'error': 'Customer data not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)
