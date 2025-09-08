"""
Customer API views with proper admin permissions and user integration.
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


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class CustomerListView(generics.ListAPIView):
    """
    List all customers - Admin only access.
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


class CustomerDetailView(generics.RetrieveAPIView):
    """
    Retrieve customer details - Admin only access.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Get Customer Details (Admin Only)",
        description="Get detailed information about a specific customer. Only admin users can access this endpoint.",
        responses={
            200: CustomerSerializer,
            403: {'description': 'Admin access required'},
            404: {'description': 'Customer not found'}
        },
        tags=['Customers - Admin']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CustomerUpdateView(APIView):
    """
    Update customer details - User can update their own data.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Update Customer Details",
        description="Update customer information. Users can update their own data.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Customer name'},
                    'email': {'type': 'string', 'description': 'Email address'},
                    'phone': {'type': 'string', 'description': 'Phone number'},
                    'telegram_chat_id': {'type': 'string', 'description': 'Telegram chat ID'},
                    'address': {'type': 'string', 'description': 'Address'},
                    'city': {'type': 'string', 'description': 'City'},
                    'country': {'type': 'string', 'description': 'Country'},
                    'postal_code': {'type': 'string', 'description': 'Postal code'}
                }
            }
        },
        responses={
            200: CustomerSerializer,
            400: {'description': 'Validation error'},
            403: {'description': 'Permission denied'},
            404: {'description': 'Customer not found'}
        },
        tags=['Customers']
    )
    def put(self, request, pk):
        """Update customer details."""
        try:
            customer = get_object_or_404(Customer, pk=pk)
            
            # Check if user can update this customer (own data or admin)
            user_customer = Customer.objects.filter(email=request.user.email).first()
            if not request.user.is_staff and customer != user_customer:
                return Response({
                    'error': 'You can only update your own customer data'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Update customer data
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
