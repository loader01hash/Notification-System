"""
Request logging middleware for the notification system.
"""
import time
import logging
import json
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware for logging API requests and responses."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Log incoming request details."""
        # Only log API requests
        if request.path.startswith('/api/'):
            request.start_time = time.time()
            
            # Log request details
            log_data = {
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
                'ip': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'content_type': request.META.get('CONTENT_TYPE', ''),
            }
            
            # Log request body for non-GET requests (but exclude sensitive data)
            if request.method != 'GET' and hasattr(request, 'body'):
                try:
                    body = json.loads(request.body.decode('utf-8'))
                    # Remove sensitive fields
                    sensitive_fields = ['password', 'token', 'secret', 'key']
                    for field in sensitive_fields:
                        if field in body:
                            body[field] = '[REDACTED]'
                    log_data['body'] = body
                except (json.JSONDecodeError, UnicodeDecodeError):
                    log_data['body'] = '[NON_JSON_BODY]'
            
            logger.info(f"Incoming request: {json.dumps(log_data)}")
    
    def process_response(self, request, response):
        """Log response details."""
        # Only log API responses
        if request.path.startswith('/api/') and hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            log_data = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'content_type': response.get('Content-Type', ''),
            }
            
            # Log response size
            if hasattr(response, 'content'):
                log_data['response_size'] = len(response.content)
            
            # Determine log level based on status code
            if response.status_code >= 500:
                logger.error(f"Response: {json.dumps(log_data)}")
            elif response.status_code >= 400:
                logger.warning(f"Response: {json.dumps(log_data)}")
            else:
                logger.info(f"Response: {json.dumps(log_data)}")
        
        return response
    
    def _get_client_ip(self, request):
        """Get the client's IP address."""
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
