"""
Customer URLs configuration.
"""
from django.urls import path
from .views import (
    CustomerListCreateView,
    CustomerDetailView as CustomerAPIDetailView,
    CustomerPreferencesView,
    CustomerNotificationHistoryView
)
from .admin_views import (
    CustomerListView,
    CustomerDetailView,
    CustomerUpdateView,
    CustomerDeleteView,
    MyCustomerDataView
)

app_name = 'customers'

urlpatterns = [
    # API endpoints
    path('', CustomerListCreateView.as_view(), name='customer-list'),
    path('<uuid:pk>/', CustomerAPIDetailView.as_view(), name='customer-detail'),
    path('<uuid:pk>/preferences/', CustomerPreferencesView.as_view(), name='customer-preferences'),
    path('<uuid:pk>/notifications/', CustomerNotificationHistoryView.as_view(), name='customer-notifications'),
    
    # Admin-only endpoints
    path('admin/list/', CustomerListView.as_view(), name='admin-customer-list'),
    path('admin/<uuid:pk>/', CustomerDetailView.as_view(), name='admin-customer-detail'),
    path('admin/<uuid:pk>/delete/', CustomerDeleteView.as_view(), name='admin-customer-delete'),
    
    # User endpoints
    path('me/', MyCustomerDataView.as_view(), name='my-customer-data'),
    path('<uuid:pk>/update/', CustomerUpdateView.as_view(), name='customer-update'),
]
