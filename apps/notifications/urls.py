"""
Notification URLs configuration.
"""
from django.urls import path
from .admin_views import (
    NotificationAdminSendView, NotificationAdminBulkSendView, NotificationAdminListView,
    NotificationAdminDetailView, NotificationAdminStatsView, NotificationAdminTemplateListView
)
from .user_views import (
    NotificationUserListView, NotificationUserPreferencesView
)

app_name = 'notifications'

urlpatterns = [
    # ===============================
    # USER NOTIFICATION ENDPOINTS
    # ===============================
    path('my/', NotificationUserListView.as_view(), name='my-notifications'),
    path('preferences/', NotificationUserPreferencesView.as_view(), name='my-preferences'),
    
    # ===============================
    # ADMIN NOTIFICATION ENDPOINTS
    # ===============================
    path('admin/send/', NotificationAdminSendView.as_view(), name='admin-send-notification'),
    path('admin/send-bulk/', NotificationAdminBulkSendView.as_view(), name='admin-send-bulk-notification'),
    path('admin/list/', NotificationAdminListView.as_view(), name='admin-notification-list'),
    path('admin/templates/', NotificationAdminTemplateListView.as_view(), name='admin-template-list'),
    path('admin/statistics/', NotificationAdminStatsView.as_view(), name='admin-notification-stats'),
]
