"""
Order URLs configuration.
"""
from django.urls import path
from . import views
from .admin_views import (
    OrderAdminListView, OrderAdminCreateView, OrderAdminDetailView,
    OrderAdminUpdateView, OrderAdminDeleteView, OrderAdminStatusUpdateView
)

app_name = 'orders'

urlpatterns = [
    # ===============================
    # USER ORDER ENDPOINTS 
    # ===============================
    path('my/', views.OrderUserListView.as_view(), name='my-orders'),
    path('create/', views.OrderUserCreateView.as_view(), name='create-order'),
    path('my/<str:order_number>/', views.OrderUserDetailView.as_view(), name='order-detail'),
    path('my/<str:order_number>/items/', views.OrderUserItemsView.as_view(), name='order-items'),
    path('my/<str:order_number>/cancel/', views.OrderUserCancelView.as_view(), name='cancel-order'),
    path('my/<str:order_number>/tracking/', views.OrderUserTrackingView.as_view(), name='track-order'),
    
    # ===============================
    # ADMIN ORDER ENDPOINTS
    # ===============================
    path('admin/', OrderAdminListView.as_view(), name='admin-orders-list'),
    path('admin/create/', OrderAdminCreateView.as_view(), name='admin-order-create'),
    path('admin/<str:order_number>/', OrderAdminDetailView.as_view(), name='admin-order-detail'),
    path('admin/<str:order_number>/update/', OrderAdminUpdateView.as_view(), name='admin-order-update'),
    path('admin/<str:order_number>/delete/', OrderAdminDeleteView.as_view(), name='admin-order-delete'),
    path('admin/<str:order_number>/status/', OrderAdminStatusUpdateView.as_view(), name='admin-order-status'),
]
