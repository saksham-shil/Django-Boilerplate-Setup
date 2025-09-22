from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import ValidationError, NotFound, AuthenticationFailed, NotAuthenticated, PermissionDenied, Throttled
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied as DjangoPermissionDenied
from django.http import Http404
import logging

from .responses import error_response, validation_error_response
from .constants import (
    ERROR_INTERNAL_SERVER, 
    ERROR_INPUT,
    ERROR_AUTH_CREDENTIALS_NOT_PROVIDED,
    ERROR_INVALID_CREDENTIALS,
    ERROR_PERMISSION_DENIED,
    ERROR_RATE_LIMIT_EXCEEDED
)
from rest_framework.exceptions import APIException


class APIError(APIException):
    """
    Simple custom exception that works with our response system.
    Always returns HTTP 200 with standardized error format.
    """
    status_code = 200  # Always return 200
    
    def __init__(self, message_code, detail=None, errors=None):
        self.message_code = message_code
        self.errors = errors
        
        if detail:
            self.detail = detail
        else:
            from .constants import get_message
            self.detail = get_message(message_code) 

logger = logging.getLogger("api_errors")


def custom_exception_handler(exc, context):
    """
    Global exception handler that converts all exceptions to standardized responses.
    Configure this in Django settings to handle all API exceptions automatically.
    """
    
    # Handle our custom APIError
    if isinstance(exc, APIError):
        logger.error(f"API Error: {exc.message_code} - {exc.detail}")
        return error_response(
            message_code=exc.message_code,
            message=str(exc.detail),
            errors=exc.errors if exc.errors else None
        )
    
    # Handle JWT authentication errors (invalid/expired tokens)
    if isinstance(exc, (InvalidToken, TokenError)):
        logger.warning(f"Invalid Token Error: {str(exc)}")
        return error_response(ERROR_AUTH_CREDENTIALS_NOT_PROVIDED)
    
    # Handle DRF authentication errors (no credentials provided)
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        logger.warning(f"Authentication Failed: {str(exc)}")
        return error_response(ERROR_AUTH_CREDENTIALS_NOT_PROVIDED)
    
    # Handle permission denied errors
    if isinstance(exc, (PermissionDenied, DjangoPermissionDenied)):
        logger.warning(f"Permission Denied: {str(exc)}")
        return error_response(ERROR_PERMISSION_DENIED)
    
    # Handle rate limiting errors
    if isinstance(exc, Throttled):
        logger.warning(f"Rate Limit Exceeded: {str(exc)}")
        return error_response(ERROR_RATE_LIMIT_EXCEEDED)
    
    # Handle DRF validation errors
    if isinstance(exc, ValidationError):
        logger.warning(f"Validation Error: {exc.detail}")
        return validation_error_response(errors=exc.detail)
    
    # Handle not found errors
    if isinstance(exc, (NotFound, Http404, ObjectDoesNotExist)):
        logger.warning(f"Not Found Error: {str(exc)}")
        return error_response(ERROR_INPUT)
    
    # Let DRF handle other known exceptions
    response = drf_exception_handler(exc, context)
    if response is not None:
        logger.warning(f"DRF Exception: {str(exc)}")
        return error_response(ERROR_INTERNAL_SERVER)
    
    # Handle completely unexpected exceptions
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return error_response(ERROR_INTERNAL_SERVER) 