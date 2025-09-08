"""
Customer serializers.
"""
from rest_framework import serializers
from .models import Customer


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
    """Serializer for updating customer data - excludes is_active and is_verified."""
    
    class Meta:
        model = Customer
        fields = [
            'name', 'email', 'phone', 'telegram_chat_id',
            'address', 'city', 'country', 'postal_code'
        ]
