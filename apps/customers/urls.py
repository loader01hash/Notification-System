"""
Customer URLs configuration - Separated User and Admin sections.
"""
from django.urls import path
from .views import (
    CustomerMyProfileView,
    CustomerNotificationHistoryView as UserNotificationHistoryView
)
from .admin_views import (
    CustomerAdminListView,
    CustomerAdminCreateView,
    CustomerAdminDetailView,
    CustomerAdminUpdateView,
    CustomerAdminDeleteView,
    CustomerAdminNotificationHistoryView
)

app_name = 'customers'

urlpatterns = [
    # =====================================
    # CUSTOMER - USER SECTION
    # =====================================
    
    # User's own profile management
    path('me/', CustomerMyProfileView.as_view(), name='customer-my-profile'),
    path('my-notifications/', UserNotificationHistoryView.as_view(), name='customer-my-notifications'),
    
    # =====================================
    # CUSTOMER - ADMIN SECTION  
    # =====================================
    
    # Admin customer management
    path('admin/list/', CustomerAdminListView.as_view(), name='admin-customer-list'),
    path('admin/create/', CustomerAdminCreateView.as_view(), name='admin-customer-create'),
    path('admin/<str:email>/', CustomerAdminDetailView.as_view(), name='admin-customer-detail'),
    path('admin/<str:email>/update/', CustomerAdminUpdateView.as_view(), name='admin-customer-update'),
    path('admin/<str:email>/delete/', CustomerAdminDeleteView.as_view(), name='admin-customer-delete'),
    path('admin/<str:email>/notifications/', CustomerAdminNotificationHistoryView.as_view(), name='admin-customer-notifications'),
]
