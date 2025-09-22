from rest_framework.response import Response
from .constants import get_message, is_success_code, SUCCESS_GENERIC, ERROR_GENERIC
import logging

logger = logging.getLogger("api_errors")


def success_response(message_code=SUCCESS_GENERIC, data=None, message=None):
    """
    Create a standardized success response.
    
    Args:
        message_code (int): Success message code (1000-1999)
        data (dict/list): Response data (optional)
        message (str): Custom message (optional, overrides code message)
    
    Returns:
        Response: DRF Response object with HTTP 200
    """
    
    response_data = {
        "response": "success",
        "message_code": message_code,
        "message": message or get_message(message_code)
    }
    
    if data is not None:
        response_data["data"] = data
        
    return Response(response_data, status=200)


def error_response(message_code=ERROR_GENERIC, errors=None, message=None):
    """
    Create a standardized error response.
    
    Args:
        message_code (int): Error message code (2000+)
        errors (str/list/dict): Error details (optional)
        message (str): Custom message (optional, overrides code message)
    
    Returns:
        Response: DRF Response object with HTTP 200
    """
    response_data = {
        "response": "error", 
        "message_code": message_code,
        "message": message or get_message(message_code)
    }
    
    if errors is not None:
        response_data["errors"] = errors
        
    return Response(response_data, status=200)


def validation_error_response(errors, message_code=None):
    """
    Create a validation error response from serializer errors.
    
    Args:
        errors (dict/list): Validation errors from serializer
        message_code (int): Custom message code (optional)
        
    Returns:
        Response: DRF Response object with HTTP 200
    """
    from .constants import ERROR_VALIDATION
    
    return error_response(
        message_code=message_code or ERROR_VALIDATION,
        errors=errors
    )