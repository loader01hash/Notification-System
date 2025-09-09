"""
Customer API views - User Section.
"""
from rest_framework import generics, permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from .models import Customer
from apps.notifications.models import NotificationPreference


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model."""
    
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'email', 'phone', 'telegram_chat_id',
            'address', 'city', 'country', 'postal_code',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomerUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating customer details."""
    
    class Meta:
        model = Customer
        fields = [
            'name', 'phone', 'telegram_chat_id',
            'address', 'city', 'country', 'postal_code'
        ]
        # Email is excluded from updates for security


class CustomerMyProfileView(APIView):
    """API view for user to manage their own customer profile."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get My Customer Profile",
        description="Get customer profile for the authenticated user.",
        responses={
            200: CustomerSerializer,
            404: {'description': 'Customer profile not found'}
        },
        tags=['Customers - User']
    )
    def get(self, request):
        """Get authenticated user's customer profile."""
        try:
            customer = Customer.objects.get(email=request.user.email)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response({
                'error': 'Customer profile not found for this user',
                'message': 'Please create a customer profile first'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @extend_schema(
        summary="Update My Customer Profile",
        description="Update customer profile for the authenticated user.",
        request=CustomerUpdateSerializer,
        responses={
            200: CustomerSerializer,
            400: {'description': 'Validation error'},
            404: {'description': 'Customer profile not found'}
        },
        tags=['Customers - User']
    )
    def put(self, request):
        """Update authenticated user's customer profile - Full update."""
        try:
            customer = Customer.objects.get(email=request.user.email)
            serializer = CustomerUpdateSerializer(customer, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                # Return full customer data
                full_serializer = CustomerSerializer(customer)
                return Response(full_serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Customer.DoesNotExist:
            return Response({
                'error': 'Customer profile not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @extend_schema(
        summary="Partially Update My Customer Profile",
        description="Partially update customer profile for the authenticated user.",
        request=CustomerUpdateSerializer,
        responses={
            200: CustomerSerializer,
            400: {'description': 'Validation error'},
            404: {'description': 'Customer profile not found'}
        },
        tags=['Customers - User']
    )
    def patch(self, request):
        """Update authenticated user's customer profile - Partial update."""
        try:
            customer = Customer.objects.get(email=request.user.email)
            serializer = CustomerUpdateSerializer(customer, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                # Return full customer data
                full_serializer = CustomerSerializer(customer)
                return Response(full_serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Customer.DoesNotExist:
            return Response({
                'error': 'Customer profile not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)


class CustomerNotificationHistoryView(APIView):
    """API view for user's notification history."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get My Notification History",
        description="Get notification history for the authenticated user.",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'customer_id': {'type': 'string'},
                    'customer_name': {'type': 'string'},
                    'history': {'type': 'array', 'items': {'type': 'object'}}
                }
            },
            404: {'description': 'Customer profile not found'}
        },
        tags=['Customers - User']
    )
    def get(self, request):
        """Get notification history for authenticated user."""
        try:
            customer = Customer.objects.get(email=request.user.email)
            limit = int(request.query_params.get('limit', 10))
            
            # Import notification service
            from apps.notifications.services import NotificationAnalyticsService
            from apps.notifications.models import Notification
            
            # Get actual notification history
            notifications = Notification.objects.filter(
                customer=customer
            ).select_related('template', 'order').order_by('-created_at')[:limit]
            
            history = []
            for notification in notifications:
                history.append({
                    'id': str(notification.id),
                    'template_name': notification.template.name,
                    'channel': notification.template.channel,
                    'subject': notification.subject,
                    'message': notification.message[:100] + ('...' if len(notification.message) > 100 else ''),
                    'status': notification.status,
                    'priority': notification.priority,
                    'recipient': notification.recipient,
                    'order_number': notification.order.order_number if notification.order else None,
                    'created_at': notification.created_at.isoformat(),
                    'sent_at': notification.sent_at.isoformat() if notification.sent_at else None,
                    'delivered_at': notification.delivered_at.isoformat() if notification.delivered_at else None,
                    'retry_count': notification.retry_count,
                    'error_message': notification.error_message if notification.error_message else None
                })
            
            return Response({
                'customer_id': str(customer.id),
                'customer_name': customer.name,
                'history': history,
                'total_count': notifications.count(),
                'message': f'Found {len(history)} notifications' if history else 'No notifications found'
            })
            
        except Customer.DoesNotExist:
            return Response({
                'error': 'Customer profile not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'Could not load notification history: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
