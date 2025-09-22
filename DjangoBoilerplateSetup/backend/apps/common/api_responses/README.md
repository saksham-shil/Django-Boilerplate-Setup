# Standardized API Response System

This module provides a standardized API response system that ensures all responses follow a consistent format and return HTTP 200 status code.

## Features

- All responses return HTTP 200 status code
- Success/error differentiated by `response` field and `message_code`
- Consistent response format across all endpoints
- Integration with drf-spectacular for API documentation
- Custom exception handler for automatic error conversion

## Response Format

### Success Response (with data)
```json
{
  "response": "success",
  "message_code": 1001,
  "message": "User login successful",
  "data": {"user_id": 123, "username": "john_doe"}
}
```

### Success Response (without data)
```json
{
  "response": "success",
  "message_code": 1006,
  "message": "Data deleted successfully"
}
```

### Error Response (with details)
```json
{
  "response": "error",
  "message_code": 2001,
  "message": "Validation error occurred",
  "errors": ["Username is required", "Password too short"]
}
```

### Error Response (without details)
```json
{
  "response": "error",
  "message_code": 2004,
  "message": "User not found"
}
```

## Usage

### 1. Using Response Functions (Recommended)

```python
from apps.common.api_responses.responses import success_response, error_response
from apps.common.api_responses.constants import LOGIN_SUCCESSFUL, AUTHENTICATION_FAILED

def login_view(request):
    if user_authenticated:
        return success_response(
            LOGIN_SUCCESSFUL,
            {'user_id': user.id, 'username': user.username}
        )
    else:
        return error_response(AUTHENTICATION_FAILED)
```

### 2. Using Mixin

```python
from apps.common.api_responses.mixins import StandardResponseMixin
from apps.common.api_responses.constants import DATA_RETRIEVED, USER_NOT_FOUND

class UserView(StandardResponseMixin, generics.GenericAPIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            return self.success_response(DATA_RETRIEVED, user_data)
        except User.DoesNotExist:
            return self.error_response(USER_NOT_FOUND)
```

### 3. Validation Errors

```python
from apps.common.api_responses.responses import validation_error_response

def create_user(request):
    serializer = UserSerializer(data=request.data)
    if not serializer.is_valid():
        return validation_error_response(serializer.errors)
    
    # ... rest of logic
```

## Message Codes

### Success Codes (1000-1999)
- `SUCCESS_GENERIC` (1000): Operation completed successfully
- `LOGIN_SUCCESSFUL` (1001): User login successful
- `USER_CREATED` (1003): User account created successfully
- `DATA_RETRIEVED` (1004): Data retrieved successfully
- `DATA_UPDATED` (1005): Data updated successfully
- `DATA_DELETED` (1006): Data deleted successfully

### Error Codes (2000+)
- `ERROR_GENERIC` (2000): An error occurred
- `VALIDATION_ERROR` (2001): Validation error occurred
- `AUTHENTICATION_FAILED` (2002): Authentication failed
- `USER_NOT_FOUND` (2004): User not found
- `EMAIL_ALREADY_EXISTS` (2009): Email address already exists
- `SERVER_ERROR` (2016): Internal server error

## API Documentation

For detailed API documentation with examples, use the schema serializers:

```python
from drf_spectacular.utils import extend_schema
from apps.common.api_responses.schema import DetailedSuccessResponseSerializer, DetailedErrorResponseSerializer

@extend_schema(
    responses={
        200: DetailedSuccessResponseSerializer,
        400: DetailedErrorResponseSerializer
    }
)
def my_api_view(request):
    # Your logic here
    pass
```

## Exception Handling

The system includes a custom exception handler that automatically converts all exceptions to the standardized format. This is configured in `settings.py`:

```python
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'apps.common.api_responses.exceptions.custom_exception_handler',
    # ... other settings
}
```

## Adding New Message Codes

To add new message codes, update `constants.py`:

```python
# Add new success code
NEW_SUCCESS_CODE = 1009

# Add new error code
NEW_ERROR_CODE = 2017

# Add to MESSAGES dictionary
MESSAGES = {
    # ... existing messages
    NEW_SUCCESS_CODE: "New success message",
    NEW_ERROR_CODE: "New error message",
}
``` 