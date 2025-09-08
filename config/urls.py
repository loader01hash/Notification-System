"""
URLs configuration for the notification system.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

def favicon_view(request):
    """Simple favicon handler"""
    return HttpResponse(status=204)  # No Content

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Favicon handler
    path('favicon.ico', favicon_view, name='favicon'),
    
    # Root redirect to API
    path('', RedirectView.as_view(url='/api/v1/', permanent=False), name='root'),
    
    # Health checks
    path('health/', include('health_check.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints with namespaces
    path('api/v1/', include(('apps.api_gateway.urls', 'api_gateway'), namespace='api_gateway')),
    path('api/v1/auth/', include(('apps.auth_system.urls', 'auth_system'), namespace='auth')),
    path('api/v1/notifications/', include(('apps.notifications.urls', 'notifications'), namespace='notifications')),
    path('api/v1/customers/', include(('apps.customers.urls', 'customers'), namespace='customers')),
    path('api/v1/orders/', include(('apps.orders.urls', 'orders'), namespace='orders')),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar URLs
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
