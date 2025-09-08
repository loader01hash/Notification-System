"""
API Gateway URLs configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api_gateway'

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path('metrics/', views.MetricsView.as_view(), name='metrics'),
    path('system-status/', views.SystemStatusView.as_view(), name='system-status'),
]
