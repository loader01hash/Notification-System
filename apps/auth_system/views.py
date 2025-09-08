"""
Authentication views for obtaining and managing tokens.
"""
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    TokenObtainSerializer, 
    TokenResponseSerializer, 
    UserRegistrationSerializer,
    TokenStatusSerializer,
    QuickCheckSerializer
)


class ObtainAuthTokenView(APIView):
    """
    Obtain authentication token by providing username and password.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Obtain Authentication Token",
        description="Get an authentication token by providing valid credentials",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'description': 'Username'},
                    'password': {'type': 'string', 'description': 'Password'}
                },
                'required': ['username', 'password']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string', 'description': 'Authentication token'},
                    'user_id': {'type': 'integer', 'description': 'User ID'},
                    'username': {'type': 'string', 'description': 'Username'}
                }
            },
            400: {'description': 'Invalid credentials'}
        },
        tags=['Authentication']
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'message': 'Token obtained successfully'
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CreateUserView(APIView):
    """
    Create a new user account and return authentication token.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Create User Account",
        description="Create a new user account and get authentication token",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'description': 'Username'},
                    'password': {'type': 'string', 'description': 'Password'},
                    'email': {'type': 'string', 'description': 'Email address', 'required': False},
                    'first_name': {'type': 'string', 'description': 'First name', 'required': False},
                    'last_name': {'type': 'string', 'description': 'Last name', 'required': False}
                },
                'required': ['username', 'password']
            }
        },
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string', 'description': 'Authentication token'},
                    'user_id': {'type': 'integer', 'description': 'User ID'},
                    'customer_id': {'type': 'string', 'description': 'Customer UUID'},
                    'username': {'type': 'string', 'description': 'Username'},
                    'email': {'type': 'string', 'description': 'Email address'},
                    'message': {'type': 'string', 'description': 'Success message'}
                }
            },
            400: {'description': 'Validation error'}
        },
        tags=['Authentication']
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create corresponding customer record
            from apps.customers.models import Customer
            customer_name = f"{first_name} {last_name}".strip() or username
            customer = Customer.objects.create(
                name=customer_name,
                email=email or f"{username}@example.com",
                is_active=True,
                is_verified=False
            )
            
            # Create token
            token = Token.objects.create(user=user)
            
            return Response({
                'token': token.key,
                'user_id': user.id,
                'customer_id': str(customer.id),
                'username': user.username,
                'email': user.email,
                'message': 'User and customer created successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'User creation failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TokenStatusView(APIView):
    """
    Check token status and get user information.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Check Token Status",
        description="Verify token validity and get user information",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'integer', 'description': 'User ID'},
                    'username': {'type': 'string', 'description': 'Username'},
                    'email': {'type': 'string', 'description': 'Email'},
                    'is_active': {'type': 'boolean', 'description': 'User is active'},
                    'token_valid': {'type': 'boolean', 'description': 'Token is valid'},
                    'message': {'type': 'string', 'description': 'Status message'}
                }
            }
        },
        tags=['Authentication']
    )
    def get(self, request):
        user = request.user
        return Response({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'token_valid': True,
            'message': 'Token is valid'
        })


class RefreshTokenView(APIView):
    """
    Refresh/regenerate authentication token.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Refresh Authentication Token",
        description="Generate a new authentication token (invalidates the old one)",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string', 'description': 'New authentication token'},
                    'message': {'type': 'string', 'description': 'Success message'}
                }
            }
        },
        tags=['Authentication']
    )
    def post(self, request):
        # Delete old token and create new one
        try:
            Token.objects.filter(user=request.user).delete()
            new_token = Token.objects.create(user=request.user)
            
            return Response({
                'token': new_token.key,
                'message': 'Token refreshed successfully'
            })
        except Exception as e:
            return Response(
                {'error': f'Token refresh failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class RevokeTokenView(APIView):
    """
    Revoke (delete) authentication token.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Revoke Authentication Token",
        description="Delete the current authentication token (logout)",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'description': 'Success message'}
                }
            }
        },
        tags=['Authentication']
    )
    def post(self, request):
        try:
            Token.objects.filter(user=request.user).delete()
            return Response({
                'message': 'Token revoked successfully (logged out)'
            })
        except Exception as e:
            return Response(
                {'error': f'Token revocation failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class QuickTokenView(APIView):
    """
    Quick token endpoint with proper Swagger documentation using serializers.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Quick Token Obtain",
        description="Simple endpoint to get token with username/password",
        request=TokenObtainSerializer,
        responses={
            200: TokenResponseSerializer,
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Error message'}
                }
            }
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Quick token obtain endpoint."""
        serializer = TokenObtainSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            
            response_data = {
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'message': 'Token obtained successfully'
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(
            {'error': 'Invalid credentials or missing fields'},
            status=status.HTTP_400_BAD_REQUEST
        )


class QuickCheckView(APIView):
    """
    Quick token check endpoint.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Quick Token Check",
        description="Simple endpoint to check if token is valid",
        responses={
            200: QuickCheckSerializer
        },
        tags=['Authentication']
    )
    def get(self, request):
        """Quick token check endpoint."""
        return Response({
            'valid': True,
            'user': request.user.username,
            'user_id': request.user.id
        })


# Function-based views for backward compatibility
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@extend_schema(
    summary="Quick Token Obtain (Function)",
    description="Function-based endpoint to get token with username/password",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'description': 'Username'},
                'password': {'type': 'string', 'description': 'Password'}
            },
            'required': ['username', 'password']
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'token': {'type': 'string', 'description': 'Authentication token'},
                'user_id': {'type': 'integer', 'description': 'User ID'},
                'username': {'type': 'string', 'description': 'Username'},
                'message': {'type': 'string', 'description': 'Success message'}
            }
        },
        400: {'description': 'Invalid credentials'}
    },
    tags=['Authentication']
)
def quick_token_obtain(request):
    """Simple function-based view to obtain token."""
    view = QuickTokenView()
    return view.post(request)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@extend_schema(
    summary="Quick Token Check (Function)",
    description="Function-based endpoint to check if token is valid",
    responses={
        200: {
            'type': 'object',
            'properties': {
                'valid': {'type': 'boolean', 'description': 'Token is valid'},
                'user': {'type': 'string', 'description': 'Username'},
                'user_id': {'type': 'integer', 'description': 'User ID'}
            }
        }
    },
    tags=['Authentication']
)
def quick_token_check(request):
    """Simple function-based view to check token status."""
    view = QuickCheckView()
    return view.get(request)
