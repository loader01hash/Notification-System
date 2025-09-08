"""
Customer API views.
"""
from rest_framework import generics, permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Customer
from apps.notifications.models import NotificationPreference
from apps.notifications.serializers import NotificationPreferenceSerializer
from apps.notifications.services import NotificationAnalyticsService


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model."""
    
    # Remove the problematic field temporarily
    # notification_channels = serializers.ListField(source='get_notification_channels', read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'email', 'phone', 'telegram_chat_id',
            'address', 'city', 'country', 'postal_code',
            'created_at', 'updated_at'
            # Remove 'notification_channels' temporarily
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomerListCreateView(generics.ListCreateAPIView):
    """API view to list and create customers."""
    
    queryset = Customer.objects.filter(is_active=True)
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]


class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for customer details."""
    
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]


class CustomerPreferencesView(APIView):
    """API view for customer notification preferences."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        """Get customer notification preferences."""
        customer = get_object_or_404(Customer, pk=pk)
        
        try:
            # Try to get preferences, but handle the case where the relationship might not exist
            if hasattr(customer, 'notification_preferences'):
                preferences = customer.notification_preferences
                # Use a simple dict response instead of serializer for now
                return Response({
                    'email_enabled': getattr(preferences, 'email_enabled', True),
                    'telegram_enabled': getattr(preferences, 'telegram_enabled', True),
                    'order_updates': getattr(preferences, 'order_updates', True),
                    'promotional': getattr(preferences, 'promotional', False),
                    'security_alerts': getattr(preferences, 'security_alerts', True),
                    'timezone': getattr(preferences, 'timezone', 'UTC')
                })
            else:
                # Return default preferences
                return Response({
                    'email_enabled': True,
                    'telegram_enabled': True,
                    'order_updates': True,
                    'promotional': False,
                    'security_alerts': True,
                    'timezone': 'UTC'
                })
        except Exception as e:
            # Return default preferences if any error occurs
            return Response({
                'email_enabled': True,
                'telegram_enabled': True,
                'order_updates': True,
                'promotional': False,
                'security_alerts': True,
                'timezone': 'UTC',
                'error': f'Could not load preferences: {str(e)}'
            })
    
    def post(self, request, pk):
        """Create or update customer notification preferences."""
        customer = get_object_or_404(Customer, pk=pk)
        
        preferences, created = NotificationPreference.objects.get_or_create(
            customer=customer
        )
        
        serializer = NotificationPreferenceSerializer(preferences, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class CustomerNotificationHistoryView(APIView):
    """API view for customer notification history."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        """Get customer notification history."""
        customer = get_object_or_404(Customer, pk=pk)
        limit = int(request.query_params.get('limit', 10))
        
        try:
            # Simplified response for now
            return Response({
                'customer_id': str(customer.id),
                'customer_name': customer.name,
                'history': [],  # Empty for now to avoid service dependency
                'message': 'Notification history feature coming soon'
            })
        except Exception as e:
            return Response({
                'error': f'Could not load notification history: {str(e)}',
                'customer_id': str(customer.id)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
