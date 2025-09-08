"""
Notification URLs configuration.
"""
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # User notification endpoints
    path('my/', views.MyNotificationsView.as_view(), name='my-notifications'),
    path('preferences/', views.MyNotificationPreferencesView.as_view(), name='my-preferences'),
    
    # Admin notification management
    path('admin/send/', views.SendNotificationView.as_view(), name='send-notification'),
    path('admin/send-bulk/', views.SendBulkNotificationView.as_view(), name='send-bulk-notification'),
    path('admin/list/', views.NotificationListView.as_view(), name='notification-list'),
    path('admin/<uuid:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('admin/status/<uuid:id>/', views.NotificationStatusView.as_view(), name='notification-status'),
    path('admin/<uuid:id>/retry/', views.retry_notification, name='retry-notification'),
    
    # Analytics
    path('admin/analytics/', views.NotificationAnalyticsView.as_view(), name='notification-analytics'),
    
    # Templates
    path('admin/templates/', views.NotificationTemplateListView.as_view(), name='template-list'),
    path('admin/templates/<uuid:pk>/', views.NotificationTemplateDetailView.as_view(), name='template-detail'),
]
