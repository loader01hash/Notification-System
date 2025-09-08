"""
Order URLs configuration.
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListCreateView.as_view(), name='order-list'),
    path('<uuid:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<uuid:pk>/status/', views.OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('<uuid:pk>/items/', views.OrderItemListView.as_view(), name='order-items'),
]
