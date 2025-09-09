"""
User role management models and utilities
"""
from django.contrib.auth.models import User
from django.db import models
from rest_framework import permissions


class UserRole(models.Model):
    """
    User role model to manage admin/user permissions
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('user', 'Regular User'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_roles'
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'


class IsAdminUser(permissions.BasePermission):
    """
    Enhanced admin permission class that checks:
    1. Django staff status (is_staff=True)
    2. UserRole model (role='admin')
    3. Specific username 'krushnappan' (backward compatibility)
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check Django staff status
        if request.user.is_staff:
            return True
            
        # Check specific username for backward compatibility
        if request.user.username == 'krushnappan':
            return True
            
        # Check UserRole model
        try:
            user_role = request.user.role
            return user_role.is_admin
        except UserRole.DoesNotExist:
            # If no role exists, create default 'user' role
            UserRole.objects.create(user=request.user, role='user')
            return False


def ensure_user_role(user):
    """
    Ensure user has a role assigned. Create default 'user' role if none exists.
    """
    role, created = UserRole.objects.get_or_create(
        user=user,
        defaults={'role': 'user'}
    )
    return role


def make_user_admin(username_or_user):
    """
    Utility function to make a user admin
    """
    if isinstance(username_or_user, str):
        try:
            user = User.objects.get(username=username_or_user)
        except User.DoesNotExist:
            return False, f"User '{username_or_user}' not found"
    else:
        user = username_or_user
    
    role = ensure_user_role(user)
    role.role = 'admin'
    role.save()
    
    return True, f"User '{user.username}' is now an admin"


def remove_admin_role(username_or_user):
    """
    Utility function to remove admin role from user
    """
    if isinstance(username_or_user, str):
        try:
            user = User.objects.get(username=username_or_user)
        except User.DoesNotExist:
            return False, f"User '{username_or_user}' not found"
    else:
        user = username_or_user
    
    role = ensure_user_role(user)
    role.role = 'user'
    role.save()
    
    return True, f"Admin role removed from '{user.username}'"


def is_user_admin(username_or_user):
    """
    Check if user has admin privileges
    """
    if isinstance(username_or_user, str):
        try:
            user = User.objects.get(username=username_or_user)
        except User.DoesNotExist:
            return False
    else:
        user = username_or_user
    
    # Check Django staff status
    if user.is_staff:
        return True
        
    # Check specific username
    if user.username == 'krushnappan':
        return True
        
    # Check UserRole
    try:
        return user.role.is_admin
    except UserRole.DoesNotExist:
        return False
