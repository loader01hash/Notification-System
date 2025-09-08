"""
Error handling middleware for the notification system.
"""
import logging
import traceback
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(MiddlewareMixin):
    """Middleware for centralized error handling."""
    
    def process_exception(self, request, exception):
        """Handle exceptions and return appropriate JSON responses."""
        logger.error(
            f"Unhandled exception in {request.path}: {str(exception)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        
        # Don't handle exceptions in debug mode - let Django handle them
        if hasattr(request, 'resolver_match') and request.resolver_match:
            if 'admin' in request.resolver_match.app_names:
                return None
        
        # Return JSON error response for API endpoints
        if request.path.startswith('/api/'):
            error_response = {
                'error': {
                    'message': 'An internal server error occurred',
                    'type': 'internal_server_error',
                    'code': 500
                }
            }
            
            # Add more specific error information in debug mode
            if hasattr(request, 'debug') and request.debug:
                error_response['error']['details'] = str(exception)
                error_response['error']['traceback'] = traceback.format_exc()
            
            return JsonResponse(
                error_response,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return None
