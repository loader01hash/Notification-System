"""
Notification API views - Admin Section.
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from .models import Notification, NotificationTemplate, NotificationPreference
from .serializers import (
    NotificationSerializer, NotificationTemplateSerializer,
    SendNotificationSerializer, SendBulkNotificationSerializer,
    NotificationPreferenceSerializer
)
from .services import NotificationService, NotificationAnalyticsService
from .tasks import send_notification_task, send_bulk_notifications_task
from apps.customers.models import Customer
from apps.auth_system.models import IsAdminUser


class NotificationAdminSendView(APIView):
    """Send notifications - Admin only."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        summary="Send Notification (Admin Only)",
        description="Send a single notification to any recipient. Only admin users can access this endpoint.",
        request=SendNotificationSerializer,
        responses={
            201: NotificationSerializer,
            403: {'description': 'Admin access required'}
        },
        tags=['Notifications - Admin']
    )
    def post(self, request):
        """Send a notification (admin only)."""
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = NotificationService()
        
        # Get related objects if provided
        customer = None
        order = None
        
        if serializer.validated_data.get('customer_id'):
            customer = get_object_or_404(Customer, id=serializer.validated_data['customer_id'])
        
        if serializer.validated_data.get('order_id'):
            from apps.orders.models import Order
            order = get_object_or_404(Order, id=serializer.validated_data['order_id'])
        
        try:
            # Create notification using template
            notification = service.create_notification(
                template_name=serializer.validated_data['template_name'],
                recipient=serializer.validated_data['recipient'],
                customer=customer,
                order=order,
                context=serializer.validated_data.get('context', {}),
                priority=serializer.validated_data.get('priority', 'normal'),
                scheduled_at=serializer.validated_data.get('scheduled_at')
            )
            
            if not notification:
                return Response({
                    'error': 'Failed to create notification'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Send the notification
            success = service.send_notification(notification)
            
            if not success:
                return Response({
                    'error': 'Failed to send notification'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Serialize and return
            response_serializer = NotificationSerializer(notification)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Failed to send notification: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationAdminBulkSendView(APIView):
    """Send bulk notifications - Admin only."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        summary="Send Bulk Notifications (Admin Only)",
        description="Send multiple notifications at once. Only admin users can access this endpoint.",
        request=SendBulkNotificationSerializer,
        responses={
            202: {'description': 'Bulk notifications queued'},
            403: {'description': 'Admin access required'}
        },
        tags=['Notifications - Admin']
    )
    def post(self, request):
        """Send bulk notifications (admin only)."""
        serializer = SendBulkNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Queue bulk notification task
            task = send_bulk_notifications_task.apply_async(
                args=[serializer.validated_data['notifications']],
                countdown=2
            )
            
            return Response({
                'message': f'Bulk notifications queued successfully',
                'task_id': task.id,
                'count': len(serializer.validated_data['notifications'])
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            return Response({
                'error': f'Failed to queue bulk notifications: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationAdminListView(generics.ListAPIView):
    """List all notifications - Admin only."""
    
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        summary="List All Notifications (Admin Only)",
        description="Get a list of all notifications in the system. Only admin users can access this endpoint.",
        responses={
            200: NotificationSerializer(many=True),
            403: {'description': 'Admin access required'}
        },
        tags=['Notifications - Admin']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class NotificationAdminDetailView(generics.RetrieveAPIView):
    """View any notification details - Admin only."""
    
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        summary="Get Any Notification Details (Admin Only)",
        description="Get detailed information about any notification. Only admin users can access this endpoint.",
        responses={
            200: NotificationSerializer,
            403: {'description': 'Admin access required'},
            404: {'description': 'Notification not found'}
        },
        tags=['Notifications - Admin']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class NotificationAdminStatsView(APIView):
    """Get notification statistics - Admin only."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        summary="Get Notification Statistics (Admin Only)",
        description="Get comprehensive notification statistics. Only admin users can access this endpoint.",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'total_notifications': {'type': 'integer'},
                    'by_status': {'type': 'object'},
                    'by_type': {'type': 'object'},
                    'recent_activity': {'type': 'array'}
                }
            },
            403: {'description': 'Admin access required'}
        },
        tags=['Notifications - Admin']
    )
    def get(self, request):
        """Get notification statistics (admin only)."""
        try:
            analytics = NotificationAnalyticsService()
            stats = analytics.get_comprehensive_stats()
            return Response(stats)
        except Exception as e:
            return Response({
                'error': f'Failed to get statistics: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationAdminCustomerPreferencesView(APIView):
    """Manage any customer's notification preferences - Admin only."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        summary="Get Any Customer's Notification Preferences (Admin Only)",
        description="Get notification preferences for any customer. Only admin users can access this endpoint.",
        responses={
            200: NotificationPreferenceSerializer,
            403: {'description': 'Admin access required'},
            404: {'description': 'Customer not found'}
        },
        tags=['Notifications - Admin']
    )
    def get(self, request, customer_id):
        """Get any customer's notification preferences (admin only)."""
        try:
            customer = get_object_or_404(Customer, id=customer_id)
            preferences, _ = NotificationPreference.objects.get_or_create(
                customer=customer,
                defaults={
                    'email_enabled': True,
                    'telegram_enabled': True,
                    'order_updates': True,
                    'promotional': False,
                    'security_alerts': True
                }
            )
            
            serializer = NotificationPreferenceSerializer(preferences)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({
                'error': f'Failed to get preferences: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Update Any Customer's Notification Preferences (Admin Only)",
        description="Update notification preferences for any customer. Only admin users can access this endpoint.",
        request=NotificationPreferenceSerializer,
        responses={
            200: NotificationPreferenceSerializer,
            403: {'description': 'Admin access required'},
            404: {'description': 'Customer not found'}
        },
        tags=['Notifications - Admin']
    )
    def put(self, request, customer_id):
        """Update any customer's notification preferences (admin only)."""
        try:
            customer = get_object_or_404(Customer, id=customer_id)
            preferences, _ = NotificationPreference.objects.get_or_create(
                customer=customer
            )
            
            serializer = NotificationPreferenceSerializer(preferences, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': f'Failed to update preferences: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationAdminTemplateListView(generics.ListCreateAPIView):
    """Manage notification templates - Admin only."""
    
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        summary="List/Create Notification Templates (Admin Only)",
        description="List all notification templates or create new ones. Only admin users can access this endpoint.",
        responses={
            200: NotificationTemplateSerializer(many=True),
            201: NotificationTemplateSerializer,
            403: {'description': 'Admin access required'}
        },
        tags=['Notifications - Admin']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
