"""
Mixin for views to use standardized responses
"""

from .responses import success_response, error_response, validation_error_response


class StandardResponseMixin:
    """Mixin that provides standardized response methods for views"""
    
    def success_response(self, message_code, data=None, message=None):
        """Return a standardized success response"""
        return success_response(message_code, data, message)
    
    def error_response(self, message_code, errors=None, message=None):
        """Return a standardized error response"""
        return error_response(message_code, errors, message)
    
    def validation_error_response(self, errors, message_code=None):
        """Return a standardized validation error response"""
        return validation_error_response(errors, message_code) 