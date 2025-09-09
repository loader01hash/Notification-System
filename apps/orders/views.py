"""
Order API views.
"""
from rest_framework import generics, permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from .models import Order, OrderItem
from apps.customers.models import Customer
from apps.auth_system.models import IsAdminUser


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""
    
    class Meta:
        model = OrderItem
        fields = ['product_name', 'quantity', 'unit_price']
        read_only_fields = ['total_price']


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


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders - simple items structure."""
    
    items = OrderItemSerializer(many=True, write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'status', 'currency',
            'shipping_address', 'shipping_method', 'notes', 'items'
        ]
        extra_kwargs = {
            'currency': {'default': 'INR'},
            'status': {'default': 'pending'}
        }
    
    def validate_items(self, items):
        """Basic validation for items."""
        if not items:
            raise serializers.ValidationError("At least one item is required.")
        return items
    
    def create(self, validated_data):
        """Create order with items and auto-calculated total."""
        request = self.context.get('request')
        items_data = validated_data.pop('items', [])
        
        # Calculate total amount from items
        total_amount = sum(
            item['quantity'] * item['unit_price'] 
            for item in items_data
        )
        validated_data['total_amount'] = total_amount
        
        # Get customer from authenticated user's email
        try:
            from apps.customers.models import Customer
            customer = Customer.objects.get(email=request.user.email)
            validated_data['customer'] = customer
        except Customer.DoesNotExist:
            raise serializers.ValidationError(
                "No customer profile found for this user. Please create a customer profile first."
            )
        
        # Auto-generate unique order number
        import time
        import uuid
        timestamp = int(time.time())
        random_part = str(uuid.uuid4())[:8].upper()
        order_number = f"ORD-{timestamp}-{random_part}"
        validated_data['order_number'] = order_number
        
        # Set default currency if not provided
        if 'currency' not in validated_data or not validated_data['currency']:
            validated_data['currency'] = 'INR'
        
        # Create order
        order = super().create(validated_data)
        
        # Create order items (simple structure)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for order status updates."""
    
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)


class OrderUserListView(generics.ListAPIView):
    """List user's own orders."""
    
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get orders for the authenticated user's customer profile."""
        try:
            from apps.customers.models import Customer
            customer = Customer.objects.get(email=self.request.user.email)
            queryset = Order.objects.select_related('customer').filter(customer=customer)
        except Customer.DoesNotExist:
            return Order.objects.none()
        
        # Optional filtering by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    @extend_schema(
        summary="List My Orders",
        description="Get a list of orders for the authenticated user.",
        responses={200: OrderSerializer(many=True)},
        tags=['Orders - User']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class OrderUserCreateView(APIView):
    """Create orders for authenticated user."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Create My Order",
        description="Create a new order. Customer is automatically assigned from authenticated user.",
        request=OrderCreateSerializer,
        responses={
            201: OrderSerializer,
            400: {'description': 'Validation error'},
            404: {'description': 'Customer profile not found for user'}
        },
        tags=['Orders - User']
    )
    def post(self, request):
        """Create order for authenticated user."""
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            # Auto-generate tracking number
            import uuid
            import time
            tracking_number = f"TRK{int(time.time())}{str(uuid.uuid4())[:8].upper()}"
            
            # Save order with tracking number
            order = serializer.save(tracking_number=tracking_number)
            
            # Trigger order creation notification
            try:
                from apps.notifications.tasks import send_order_confirmation_notification
                send_order_confirmation_notification.apply_async(
                    args=[str(order.id)],
                    countdown=2
                )
            except Exception as e:
                print(f"Failed to queue order notification: {e}")
            
            # Return full order data
            response_serializer = OrderSerializer(order)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderUserDetailView(generics.RetrieveAPIView):
    """View user's own order details by order number."""
    
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_number'
    
    def get_queryset(self):
        """Get orders for the authenticated user's customer profile."""
        try:
            from apps.customers.models import Customer
            customer = Customer.objects.get(email=self.request.user.email)
            return Order.objects.select_related('customer').prefetch_related('items').filter(customer=customer)
        except Customer.DoesNotExist:
            return Order.objects.none()
    
    @extend_schema(
        summary="Get My Order Details",
        description="Get details of a specific order by order number belonging to the authenticated user.",
        responses={
            200: OrderSerializer,
            404: {'description': 'Order not found or not owned by user'}
        },
        tags=['Orders - User']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class OrderUserItemsView(generics.ListAPIView):
    """List items for user's own orders by order number."""
    
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get order items for user's own orders by order number."""
        try:
            from apps.customers.models import Customer
            customer = Customer.objects.get(email=self.request.user.email)
            order_number = self.kwargs['order_number']
            
            # Verify order belongs to user
            try:
                order = Order.objects.get(order_number=order_number, customer=customer)
                return OrderItem.objects.filter(order=order).order_by('created_at')
            except Order.DoesNotExist:
                return OrderItem.objects.none()
        except Customer.DoesNotExist:
            return OrderItem.objects.none()
    
    @extend_schema(
        summary="List Items for My Order",
        description="Get order items for a specific order by order number belonging to the authenticated user.",
        responses={
            200: OrderItemSerializer(many=True),
            404: {'description': 'Order not found or not owned by user'}
        },
        tags=['Orders - User']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for order details."""
    
    queryset = Order.objects.select_related('customer').prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Admin only for update and delete operations
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        else:
            # Anyone authenticated can view orders
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @extend_schema(
        summary="Update Order (Admin Only)",
        description="Update order details. Only admin users can perform this action.",
        responses={
            200: OrderSerializer,
            403: {'description': 'Admin access required'},
            404: {'description': 'Order not found'}
        },
        tags=['Orders - Admin']
    )
    def put(self, request, *args, **kwargs):
        """Update order (admin only)."""
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partial Update Order (Admin Only)",
        description="Partially update order details. Only admin users can perform this action.",
        responses={
            200: OrderSerializer,
            403: {'description': 'Admin access required'},
            404: {'description': 'Order not found'}
        },
        tags=['Orders - Admin']
    )
    def patch(self, request, *args, **kwargs):
        """Partially update order (admin only)."""
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Order (Admin Only)",
        description="Delete order. Only admin users can perform this action.",
        responses={
            204: {'description': 'Order deleted successfully'},
            403: {'description': 'Admin access required'},
            404: {'description': 'Order not found'}
        },
        tags=['Orders - Admin']
    )
    def delete(self, request, *args, **kwargs):
        """Delete order (admin only)."""
        return super().delete(request, *args, **kwargs)


class OrderStatusUpdateView(APIView):
    """API view to update order status - Admin only."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    serializer_class = OrderStatusUpdateSerializer
    
    @extend_schema(
        summary="Update Order Status (Admin Only)",
        description="Update order status. Only admin users (staff or 'krushnappan') can perform this action.",
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
    def put(self, request, pk):
        """Update order status (admin only)."""
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


class OrderUserCancelView(APIView):
    """Cancel user's own order."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Cancel My Order",
        description="Cancel an order belonging to the authenticated user.",
        request={
            'type': 'object',
            'properties': {
                'reason': {'type': 'string', 'description': 'Reason for cancellation'},
            }
        },
        responses={
            200: OrderSerializer,
            400: {'description': 'Order cannot be cancelled'},
            404: {'description': 'Order not found or not owned by user'}
        },
        tags=['Orders - User']
    )
    def post(self, request, order_number):
        """Cancel user's own order by order number."""
        try:
            from apps.customers.models import Customer
            customer = Customer.objects.get(email=request.user.email)
            
            # Get order for the authenticated user by order number
            order = Order.objects.get(order_number=order_number, customer=customer)
            
            # Check if order can be cancelled
            if order.status in ['delivered', 'cancelled']:
                return Response(
                    {'error': 'Order cannot be cancelled in current status'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update order status
            order.status = 'cancelled'
            order.save()
            
            # Trigger cancellation notification
            try:
                from apps.notifications.tasks import send_order_status_notification
                send_order_status_notification.apply_async(
                    args=[str(order.id), 'cancelled'],
                    countdown=2
                )
            except Exception as e:
                print(f"Failed to queue cancellation notification: {e}")
            
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class OrderUserTrackingView(APIView):
    """Track user's own order."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Track My Order",
        description="Get tracking information for an order belonging to the authenticated user.",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'order_id': {'type': 'string'},
                    'tracking_number': {'type': 'string'},
                    'status': {'type': 'string'},
                    'customer_name': {'type': 'string'},
                    'total_amount': {'type': 'string'},
                    'created_at': {'type': 'string', 'format': 'date-time'},
                    'updated_at': {'type': 'string', 'format': 'date-time'},
                }
            },
            404: {'description': 'Order not found or not owned by user'}
        },
        tags=['Orders - User']
    )
    def get(self, request, order_number):
        """Get order tracking information for authenticated user by order number."""
        try:
            from apps.customers.models import Customer
            customer = Customer.objects.get(email=request.user.email)
            
            # Get order for the authenticated user by order number
            order = Order.objects.select_related('customer').get(order_number=order_number, customer=customer)
            
            tracking_data = {
                'order_number': order.order_number,
                'tracking_number': order.tracking_number,
                'status': order.status,
                'customer_name': customer.name,
                'total_amount': str(order.total_amount),
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat(),
            }
            
            return Response(tracking_data, status=status.HTTP_200_OK)
            
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
