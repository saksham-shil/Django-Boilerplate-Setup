from rest_framework import serializers
from apps.common.api_responses.exception_handler import APIError
from apps.common.api_responses.constants import (
    ERROR_USER_EMAIL_EXISTS,
    VALIDATION_FULL_NAME_NUMERIC,
    VALIDATION_CONTACT_NUMBER_INVALID
)

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "is_active",
            "full_name",
            "contact_number",
            "role",
            "review_status",
            "created_at",
            "updated_at"
        ]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)
    full_name = serializers.CharField(max_length=150)
    contact_number = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise APIError(ERROR_USER_EMAIL_EXISTS)
        return value

    def validate_full_name(self, value):
        if value.isdigit():
            raise APIError(VALIDATION_FULL_NAME_NUMERIC)
        return value

    def validate_contact_number(self, value):
        if value and not value.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise APIError(VALIDATION_CONTACT_NUMBER_INVALID)
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    uidb64 = serializers.CharField()
    new_password = serializers.CharField(min_length=8)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)