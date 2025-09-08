"""
Order API views.
"""
from rest_framework import generics, permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from .models import Order, OrderItem
from apps.customers.models import Customer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 'product_sku', 'quantity',
            'unit_price', 'total_price', 'product_details', 'created_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_name', 'customer_email',
            'status', 'total_amount', 'currency', 'shipping_address',
            'shipping_method', 'tracking_number', 'notes',
            'created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at',
            'items'
        ]
        read_only_fields = [
            'id', 'customer_name', 'customer_email', 'created_at', 'updated_at',
            'confirmed_at', 'shipped_at', 'delivered_at'
        ]


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for order status updates."""
    
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)


class OrderListCreateView(generics.ListCreateAPIView):
    """API view to list and create orders."""
    
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get filtered orders."""
        queryset = Order.objects.select_related('customer')
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for order details."""
    
    queryset = Order.objects.select_related('customer').prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderStatusUpdateView(APIView):
    """API view to update order status."""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderStatusUpdateSerializer
    
    @extend_schema(
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
            }
        },
        description='Update order status'
    )
    def put(self, request, pk):
        """Update order status."""
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            old_status = order.status
            
            # Update status
            order.update_status(new_status)
            
            return Response({
                'message': f'Order status updated from {old_status} to {new_status}',
                'order_id': str(order.id),
                'old_status': old_status,
                'new_status': new_status
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderItemListView(generics.ListAPIView):
    """API view to list order items."""
    
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get order items for specific order."""
        order_id = self.kwargs['pk']
        return OrderItem.objects.filter(order_id=order_id).order_by('created_at')
