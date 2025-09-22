from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample


# Only use these if you need detailed documentation for specific endpoints
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Success Response',
            value={
                "response": "success",
                "message_code": 1001,
                "message": "User login successful",
                "data": {"user_id": 123, "username": "john_doe"}
            }
        )
    ]
)
class DetailedSuccessResponseSerializer(serializers.Serializer):
    """Detailed schema for complex APIs that need examples."""
    response = serializers.CharField(default='success')
    message_code = serializers.IntegerField()
    message = serializers.CharField()
    data = serializers.JSONField(required=False)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Error Response',
            value={
                "response": "error",
                "message_code": 2002,
                "message": "Authentication failed",
                "errors": ["Invalid username or password"]
            }
        )
    ]
)
class DetailedErrorResponseSerializer(serializers.Serializer):
    """Detailed schema for complex APIs that need examples."""
    response = serializers.CharField(default='error')
    message_code = serializers.IntegerField()
    message = serializers.CharField()
    errors = serializers.JSONField(required=False) 