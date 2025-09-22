from .exception_handler import APIError
from .constants import ERROR_INPUT
from rest_framework.exceptions import ValidationError



def get_object_or_raise(model, message_code=ERROR_INPUT, **kwargs):
    """
    Get object or raise APIError.
    
    Usage:
        user = get_object_or_raise(User, pk=user_id)
        product = get_object_or_raise(Product, PRODUCT_NOT_FOUND, slug=slug)
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise APIError(message_code)


def validate_serializer(serializer):
    """
    Validate serializer or raise validation error.
    
    Usage:
        validate_serializer(serializer)
        # If invalid, automatically raises exception
    """
    if not serializer.is_valid():
        raise ValidationError(serializer.errors)


def check_condition(condition, message_code):
    """
    Check condition or raise error.
    
    Usage:
        check_condition(user.is_active, ACCOUNT_DISABLED)
        check_condition(balance >= amount, INSUFFICIENT_BALANCE)
    """
    if not condition:
        raise APIError(message_code) 


def parse_positive_int(value, field_name="id"):
    """Safely parse a positive integer or raise APIError with ERROR_INPUT.

    Centralized helper to validate and convert identifiers coming from URL
    params or query strings. Keeps view code clean and consistent.

    Args:
        value: The incoming value to parse
        field_name: Name used in the error context message

    Returns:
        int: Parsed positive integer

    Raises:
        APIError: If the value is missing, non-numeric, or <= 0
    """
    try:
        parsed = int(value)
        if parsed <= 0:
            raise ValueError
        return parsed
    except (ValueError, TypeError) as err:
        raise APIError(ERROR_INPUT, f"Invalid {field_name}") from err