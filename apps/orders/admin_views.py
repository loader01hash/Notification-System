"""
Order API views - Admin Section.
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from .models import Order, OrderItem
from .views import OrderSerializer, OrderStatusUpdateSerializer, OrderItemSerializer
from apps.customers.models import Customer
from apps.auth_system.models import IsAdminUser


class OrderAdminListView(generics.ListAPIView):
    """List all orders - Admin only."""
    
    queryset = Order.objects.select_related('customer').prefetch_related('items').order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        summary="List All Orders (Admin Only)",
        description="Get a list of all orders in the system. Only admin users can access this endpoint.",
        responses={
            200: OrderSerializer(many=True),
            403: {'description': 'Admin access required'}
        },
        tags=['Orders - Admin']
    )
    def get(self, request, *args, **kwargs):
        # Optional filtering by customer
        customer_id = request.query_params.get('customer_id')
        if customer_id:
            self.queryset = self.queryset.filter(customer_id=customer_id)
        
        # Optional filtering by status
        status_filter = request.query_params.get('status')
        if status_filter:
            self.queryset = self.queryset.filter(status=status_filter)
        
        return super().get(request, *args, **kwargs)


class OrderAdminCreateView(APIView):
    """Create orders for any customer - Admin only."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        summary="Create Order for Any Customer (Admin Only)",
        description="Create an order for any customer. Only admin users can access this endpoint.",
        request=OrderSerializer,
        responses={
            201: OrderSerializer,
            400: {'description': 'Validation error'},
            403: {'description': 'Admin access required'}
        },
        tags=['Orders - Admin']
    )
    def post(self, request):
        """Create order for any customer (admin only)."""
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            # Admin can specify any customer
            order = serializer.save()
            
            # Auto-generate tracking number
            import uuid
            import time
            tracking_number = f"TRK{int(time.time())}{str(uuid.uuid4())[:8].upper()}"
            order.tracking_number = tracking_number
            order.save()
            
            # Return full order data
            response_serializer = OrderSerializer(order)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderAdminDetailView(generics.RetrieveAPIView):
    """View any order details by order number - Admin only."""
    
    queryset = Order.objects.select_related('customer').prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    lookup_field = 'order_number'
    
    @extend_schema(
        summary="Get Any Order Details by Order Number (Admin Only)",
        description="Get detailed information about any order by order number. Only admin users can access this endpoint.",
        responses={
            200: OrderSerializer,
            403: {'description': 'Admin access required'},
            404: {'description': 'Order not found'}
        },
        tags=['Orders - Admin']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class OrderAdminUpdateView(APIView):
    """Update any order - Admin only."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        summary="Update Any Order (Admin Only)",
        description="Update any order details. Only admin users can access this endpoint.",
        request=OrderSerializer,
        responses={
            200: OrderSerializer,
            400: {'description': 'Validation error'},
            403: {'description': 'Admin access required'},
            404: {'description': 'Order not found'}
        },
        tags=['Orders - Admin']
    )
    def put(self, request, order_number):
        """Update any order by order number (admin only) - Full update."""
        order = get_object_or_404(Order, order_number=order_number)
        serializer = OrderSerializer(order, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Partially Update Any Order by Order Number (Admin Only)",
        description="Partially update any order details by order number. Only admin users can access this endpoint.",
        request=OrderSerializer,
        responses={
            200: OrderSerializer,
            400: {'description': 'Validation error'},
            403: {'description': 'Admin access required'},
            404: {'description': 'Order not found'}
        },
        tags=['Orders - Admin']
    )
    def patch(self, request, order_number):
        """Update any order by order number (admin only) - Partial update."""
        order = get_object_or_404(Order, order_number=order_number)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderAdminDeleteView(APIView):
    """Delete any order - Admin only."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        summary="Delete Order (Admin Only)",
        description="Delete any order. Only admin users can access this endpoint.",
        responses={
            204: {'description': 'Order deleted successfully'},
            403: {'description': 'Admin access required'},
            404: {'description': 'Order not found'}
        },
        tags=['Orders - Admin']
    )
    def delete(self, request, order_number):
        """Delete any order by order number (admin only)."""
        order = get_object_or_404(Order, order_number=order_number)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderAdminStatusUpdateView(APIView):
    """Update any order status - Admin only."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        summary="Update Any Order Status (Admin Only)",
        description="Update status of any order. Only admin users can access this endpoint.",
        request=OrderStatusUpdateSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'order_id': {'type': 'string'},
                    'old_status': {'type': 'string'},
                    'new_status': {'type': 'string'}
                }
            },
            403: {'description': 'Admin access required'},
            404: {'description': 'Order not found'}
        },
        tags=['Orders - Admin']
    )
    def put(self, request, order_number):
        """Update any order status by order number (admin only)."""
        order = get_object_or_404(Order, order_number=order_number)
        serializer = OrderStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            old_status = order.status
            
            # Update status
            order.update_status(new_status)
            
            return Response({
                'message': f'Order status updated from {old_status} to {new_status}',
                'order_number': order.order_number,
                'old_status': old_status,
                'new_status': new_status
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderAdminItemsView(generics.ListAPIView):
    """List items for any order - Admin only."""
    
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Get order items for any order (admin only)."""
        order_id = self.kwargs['pk']
        return OrderItem.objects.filter(order_id=order_id).order_by('created_at')
    
    @extend_schema(
        summary="List Items for Any Order (Admin Only)",
        description="Get order items for any order. Only admin users can access this endpoint.",
        responses={
            200: OrderItemSerializer(many=True),
            403: {'description': 'Admin access required'}
        },
        tags=['Orders - Admin']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
