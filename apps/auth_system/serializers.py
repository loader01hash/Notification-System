"""
Serializers for authentication endpoints.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class TokenObtainSerializer(serializers.Serializer):
    """Serializer for token obtain endpoint."""
    username = serializers.CharField(max_length=150, help_text="Username")
    password = serializers.CharField(max_length=128, style={'input_type': 'password'}, help_text="Password")
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(request=self.context.get('request'),
                              username=username, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password')


class TokenResponseSerializer(serializers.Serializer):
    """Serializer for token response."""
    token = serializers.CharField(help_text="Authentication token")
    user_id = serializers.IntegerField(help_text="User ID")
    username = serializers.CharField(help_text="Username")
    message = serializers.CharField(help_text="Success message")


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TokenStatusSerializer(serializers.Serializer):
    """Serializer for token status response."""
    user_id = serializers.IntegerField(help_text="User ID")
    username = serializers.CharField(help_text="Username")
    email = serializers.EmailField(help_text="Email address")
    first_name = serializers.CharField(help_text="First name")
    last_name = serializers.CharField(help_text="Last name")
    is_active = serializers.BooleanField(help_text="User is active")
    token_valid = serializers.BooleanField(help_text="Token is valid")
    message = serializers.CharField(help_text="Status message")


class QuickCheckSerializer(serializers.Serializer):
    """Serializer for quick check response."""
    valid = serializers.BooleanField(help_text="Token is valid")
    user = serializers.CharField(help_text="Username")
    user_id = serializers.IntegerField(help_text="User ID")
