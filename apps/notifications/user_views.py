"""
Notification API views - User Section.
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from .models import Notification, NotificationPreference
from .serializers import (
    NotificationSerializer, NotificationPreferenceSerializer
)
from .services import NotificationAnalyticsService
from apps.customers.models import Customer


class NotificationUserListView(generics.ListAPIView):
    """List user's own notifications."""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get notifications for the authenticated user's customer profile."""
        try:
            customer = Customer.objects.get(email=self.request.user.email)
            return Notification.objects.filter(
                customer=customer
            ).order_by('-created_at')
        except Customer.DoesNotExist:
            return Notification.objects.none()
    
    @extend_schema(
        summary="List My Notifications",
        description="Get a list of notifications for the authenticated user.",
        responses={200: NotificationSerializer(many=True)},
        tags=['Notifications - User']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class NotificationUserDetailView(generics.RetrieveAPIView):
    """View user's own notification details."""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get notifications for the authenticated user's customer profile."""
        try:
            customer = Customer.objects.get(email=self.request.user.email)
            return Notification.objects.filter(customer=customer)
        except Customer.DoesNotExist:
            return Notification.objects.none()
    
    @extend_schema(
        summary="Get My Notification Details",
        description="Get details of a specific notification belonging to the authenticated user.",
        responses={
            200: NotificationSerializer,
            404: {'description': 'Notification not found or not owned by user'}
        },
        tags=['Notifications - User']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class NotificationUserStatsView(APIView):
    """Get user's notification statistics."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get My Notification Statistics",
        description="Get notification statistics for the authenticated user.",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'total_notifications': {'type': 'integer'},
                    'unread_count': {'type': 'integer'},
                    'by_status': {'type': 'object'},
                    'recent_activity': {'type': 'array'}
                }
            },
            404: {'description': 'Customer profile not found'}
        },
        tags=['Notifications - User']
    )
    def get(self, request):
        """Get notification statistics for authenticated user."""
        try:
            customer = Customer.objects.get(email=request.user.email)
            
            # Get user-specific stats
            total_notifications = Notification.objects.filter(customer=customer).count()
            unread_count = Notification.objects.filter(
                customer=customer, 
                status='pending'
            ).count()
            
            # Status breakdown
            status_counts = {}
            for status_choice in ['pending', 'sent', 'delivered', 'failed']:
                count = Notification.objects.filter(
                    customer=customer, 
                    status=status_choice
                ).count()
                status_counts[status_choice] = count
            
            # Recent notifications
            recent = Notification.objects.filter(
                customer=customer
            ).order_by('-created_at')[:5]
            
            recent_data = []
            for notification in recent:
                recent_data.append({
                    'id': str(notification.id),
                    'title': notification.title,
                    'status': notification.status,
                    'created_at': notification.created_at
                })
            
            return Response({
                'total_notifications': total_notifications,
                'unread_count': unread_count,
                'by_status': status_counts,
                'recent_activity': recent_data
            })
            
        except Customer.DoesNotExist:
            return Response({
                'error': 'Customer profile not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Failed to get statistics: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationUserPreferencesView(APIView):
    """Manage user's own notification preferences."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get My Notification Preferences",
        description="Get notification preferences for the authenticated user.",
        responses={
            200: NotificationPreferenceSerializer,
            404: {'description': 'Customer profile not found'}
        },
        tags=['Notifications - User']
    )
    def get(self, request):
        """Get notification preferences for authenticated user."""
        try:
            customer = Customer.objects.get(email=request.user.email)
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
            
        except Customer.DoesNotExist:
            return Response({
                'error': 'Customer profile not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Failed to get preferences: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Update My Notification Preferences",
        description="Update notification preferences for the authenticated user.",
        request=NotificationPreferenceSerializer,
        responses={
            200: NotificationPreferenceSerializer,
            404: {'description': 'Customer profile not found'}
        },
        tags=['Notifications - User']
    )
    def put(self, request):
        """Update notification preferences for authenticated user."""
        try:
            customer = Customer.objects.get(email=request.user.email)
            preferences, _ = NotificationPreference.objects.get_or_create(
                customer=customer
            )
            
            serializer = NotificationPreferenceSerializer(preferences, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Customer.DoesNotExist:
            return Response({
                'error': 'Customer profile not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Failed to update preferences: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Partially Update My Notification Preferences",
        description="Partially update notification preferences for the authenticated user.",
        request=NotificationPreferenceSerializer,
        responses={
            200: NotificationPreferenceSerializer,
            404: {'description': 'Customer profile not found'}
        },
        tags=['Notifications - User']
    )
    def patch(self, request):
        """Partially update notification preferences for authenticated user."""
        try:
            customer = Customer.objects.get(email=request.user.email)
            preferences, _ = NotificationPreference.objects.get_or_create(
                customer=customer
            )
            
            serializer = NotificationPreferenceSerializer(
                preferences, 
                data=request.data, 
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Customer.DoesNotExist:
            return Response({
                'error': 'Customer profile not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Failed to update preferences: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationUserMarkReadView(APIView):
    """Mark user's notifications as read."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Mark Notification as Read",
        description="Mark a specific notification as read for the authenticated user.",
        responses={
            200: {'description': 'Notification marked as read'},
            404: {'description': 'Notification not found or not owned by user'}
        },
        tags=['Notifications - User']
    )
    def patch(self, request, pk):
        """Mark notification as read."""
        try:
            customer = Customer.objects.get(email=request.user.email)
            notification = get_object_or_404(
                Notification, 
                id=pk, 
                customer=customer
            )
            
            # Update status to delivered/read
            notification.status = 'delivered'
            notification.save()
            
            return Response({
                'message': 'Notification marked as read',
                'notification_id': str(notification.id)
            })
            
        except Customer.DoesNotExist:
            return Response({
                'error': 'Customer profile not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Failed to mark notification as read: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationUserMarkAllReadView(APIView):
    """Mark all user's notifications as read."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Mark All Notifications as Read",
        description="Mark all notifications as read for the authenticated user.",
        responses={
            200: {'description': 'All notifications marked as read'},
            404: {'description': 'Customer profile not found'}
        },
        tags=['Notifications - User']
    )
    def patch(self, request):
        """Mark all notifications as read for authenticated user."""
        try:
            customer = Customer.objects.get(email=request.user.email)
            
            # Update all pending notifications to delivered
            updated_count = Notification.objects.filter(
                customer=customer,
                status='pending'
            ).update(status='delivered')
            
            return Response({
                'message': f'Marked {updated_count} notifications as read',
                'updated_count': updated_count
            })
            
        except Customer.DoesNotExist:
            return Response({
                'error': 'Customer profile not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Failed to mark notifications as read: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
