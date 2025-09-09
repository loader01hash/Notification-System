"""
Customer API views - Admin Section.
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from .models import Customer
from .serializers import CustomerSerializer, CustomerUpdateSerializer
from apps.auth_system.models import IsAdminUser


class CustomerAdminListView(generics.ListAPIView):
    """
    List all customers - Admin only.
    """
    queryset = Customer.objects.all().order_by('-created_at')
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="List All Customers (Admin Only)",
        description="Get a list of all customers. Only admin users can access this endpoint.",
        responses={
            200: CustomerSerializer(many=True),
            403: {'description': 'Admin access required'}
        },
        tags=['Customers - Admin']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CustomerAdminCreateView(APIView):
    """
    Create customers - Admin only.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Create Customer (Admin Only)",
        description="Create a new customer. Only admin users can access this endpoint.",
        request=CustomerSerializer,
        responses={
            201: CustomerSerializer,
            400: {'description': 'Validation error'},
            403: {'description': 'Admin access required'}
        },
        tags=['Customers - Admin']
    )
    def post(self, request):
        """Create new customer (admin only)."""
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerAdminDetailView(generics.RetrieveAPIView):
    """
    Retrieve any customer details by email - Admin only.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    lookup_field = 'email'
    
    @extend_schema(
        summary="Get Any Customer Details by Email (Admin Only)",
        description="Get detailed information about any customer by email. Only admin users can access this endpoint.",
        responses={
            200: CustomerSerializer,
            403: {'description': 'Admin access required'},
            404: {'description': 'Customer not found'}
        },
        tags=['Customers - Admin']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CustomerAdminUpdateView(APIView):
    """
    Update any customer details - Admin only.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Update Any Customer Details (Admin Only)",
        description="Update any customer information. Only admin users can access this endpoint.",
        request=CustomerUpdateSerializer,
        responses={
            200: CustomerSerializer,
            400: {'description': 'Validation error'},
            403: {'description': 'Admin access required'},
            404: {'description': 'Customer not found'}
        },
        tags=['Customers - Admin']
    )
    def put(self, request, email):
        """Update any customer details by email (admin only) - Full update."""
        try:
            customer = get_object_or_404(Customer, email=email)
            serializer = CustomerUpdateSerializer(customer, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                # Return full customer data
                full_serializer = CustomerSerializer(customer)
                return Response(full_serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': f'Update failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Partially Update Any Customer Details (Admin Only)",
        description="Partially update any customer information. Only admin users can access this endpoint.",
        request=CustomerUpdateSerializer,
        responses={
            200: CustomerSerializer,
            400: {'description': 'Validation error'},
            403: {'description': 'Admin access required'},
            404: {'description': 'Customer not found'}
        },
        tags=['Customers - Admin']
    )
    def patch(self, request, pk):
        """Update any customer details (admin only) - Partial update."""
        try:
            customer = get_object_or_404(Customer, pk=pk)
            serializer = CustomerUpdateSerializer(customer, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                # Return full customer data
                full_serializer = CustomerSerializer(customer)
                return Response(full_serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': f'Update failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerAdminDeleteView(APIView):
    """
    Delete any customer - Admin only.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Delete Customer (Admin Only)",
        description="Delete customer and associated user account. Only admin users can perform this action.",
        responses={
            204: {'description': 'Customer deleted successfully'},
            403: {'description': 'Admin access required'},
            404: {'description': 'Customer not found'},
            500: {'description': 'Deletion failed'}
        },
        tags=['Customers - Admin']
    )
    def delete(self, request, email):
        """Delete customer by email and associated user (admin only)."""
        try:
            customer = get_object_or_404(Customer, email=email)
            
            # Find and delete associated user
            try:
                user = User.objects.get(email=customer.email)
                user.delete()
            except User.DoesNotExist:
                pass  # Customer exists without user, just delete customer
            
            # Delete customer
            customer.delete()
            
            return Response({
                'message': 'Customer and associated user deleted successfully'
            }, status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response({
                'error': f'Deletion failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerAdminNotificationHistoryView(APIView):
    """
    Get any customer's notification history - Admin only.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Get Any Customer's Notification History (Admin Only)",
        description="Get notification history for any customer. Only admin users can access this endpoint.",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'customer_id': {'type': 'string'},
                    'customer_name': {'type': 'string'},
                    'history': {'type': 'array', 'items': {'type': 'object'}}
                }
            },
            403: {'description': 'Admin access required'},
            404: {'description': 'Customer not found'}
        },
        tags=['Customers - Admin']
    )
    def get(self, request, email):
        """Get notification history for any customer by email (admin only)."""
        try:
            customer = get_object_or_404(Customer, email=email)
            limit = int(request.query_params.get('limit', 10))
            
            # Import notification models
            from apps.notifications.models import Notification
            
            # Get actual notification history for the specified customer
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
                'customer_email': customer.email,
                'customer_name': customer.name,
                'history': history,
                'total_count': len(history),
                'message': f'Found {len(history)} notifications for {customer.name}' if history else f'No notifications found for {customer.name}'
            })
            
        except Exception as e:
            return Response({
                'error': f'Could not load notification history: {str(e)}',
                'customer_email': email
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerDeleteView(APIView):
    """
    Delete customer and associated user - Admin only.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Delete Customer (Admin Only)",
        description="Delete customer and associated user account. Only admin users can perform this action.",
        responses={
            204: {'description': 'Customer deleted successfully'},
            403: {'description': 'Admin access required'},
            404: {'description': 'Customer not found'},
            500: {'description': 'Deletion failed'}
        },
        tags=['Customers - Admin']
    )
    def delete(self, request, pk):
        """Delete customer and associated user."""
        try:
            customer = get_object_or_404(Customer, pk=pk)
            
            # Find and delete associated user
            try:
                user = User.objects.get(email=customer.email)
                user.delete()
            except User.DoesNotExist:
                pass  # Customer exists without user, just delete customer
            
            # Delete customer
            customer.delete()
            
            return Response({
                'message': 'Customer and associated user deleted successfully'
            }, status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response({
                'error': f'Deletion failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyCustomerDataView(APIView):
    """
    Get current user's customer data.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get My Customer Data",
        description="Get customer data for the currently authenticated user.",
        responses={
            200: CustomerSerializer,
            404: {'description': 'Customer data not found for this user'}
        },
        tags=['Customers']
    )
    def get(self, request):
        """Get current user's customer data."""
        try:
            customer = Customer.objects.get(email=request.user.email)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response({
                'error': 'Customer data not found for this user'
            }, status=status.HTTP_404_NOT_FOUND)
