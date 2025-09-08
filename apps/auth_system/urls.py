"""
URL patterns for authentication endpoints.
"""
from django.urls import path
from . import views

app_name = 'auth_system'

urlpatterns = [
    # Token management endpoints
    path('token/', views.ObtainAuthTokenView.as_view(), name='obtain_token'),
    path('token/check/', views.TokenStatusView.as_view(), name='token_status'),
    path('token/refresh/', views.RefreshTokenView.as_view(), name='refresh_token'),
    path('token/revoke/', views.RevokeTokenView.as_view(), name='revoke_token'),
    
    # User management
    path('register/', views.CreateUserView.as_view(), name='register'),
    
    # Quick endpoints (class-based - better for Swagger)
    path('quick-token/', views.QuickTokenView.as_view(), name='quick_token_class'),
    path('quick-check/', views.QuickCheckView.as_view(), name='quick_check_class'),
]
