"""
Rate limiting middleware for the notification system.
"""
import time
import hashlib
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """Middleware for API rate limiting."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Apply rate limiting to API requests."""
        # Only apply rate limiting to API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        # Get client identifier
        client_id = self._get_client_identifier(request)
        
        # Check rate limit
        if self._is_rate_limited(client_id, request):
            return JsonResponse({
                'error': {
                    'message': 'Rate limit exceeded',
                    'type': 'rate_limit_exceeded',
                    'code': 429
                }
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        return None
    
    def _get_client_identifier(self, request):
        """Get unique identifier for the client."""
        # Use user ID if authenticated, otherwise use IP address
        if request.user.is_authenticated:
            return f"user_{request.user.id}"
        
        # Get IP address (handle proxy headers)
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            ip = forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        return f"ip_{ip}"
    
    def _is_rate_limited(self, client_id, request):
        """Check if client has exceeded rate limit."""
        # Different limits for different endpoints
        endpoint_limits = {
            '/api/v1/notifications/send/': {'requests': 10, 'window': 60},  # 10 per minute
            'default': {'requests': 100, 'window': 3600},  # 100 per hour
        }
        
        # Get limit for current endpoint
        limit_config = endpoint_limits.get(request.path, endpoint_limits['default'])
        
        cache_key = f"rate_limit_{client_id}_{request.path}"
        current_time = int(time.time())
        window_start = current_time - limit_config['window']
        
        # Get current request count
        requests = cache.get(cache_key, [])
        
        # Remove old requests outside the window
        requests = [req_time for req_time in requests if req_time > window_start]
        
        # Check if limit exceeded
        if len(requests) >= limit_config['requests']:
            logger.warning(f"Rate limit exceeded for {client_id} on {request.path}")
            return True
        
        # Add current request and update cache
        requests.append(current_time)
        cache.set(cache_key, requests, limit_config['window'])
        
        return False
