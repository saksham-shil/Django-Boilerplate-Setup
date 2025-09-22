import os
import uuid
from django.db import transaction
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from apps.common.api_responses.exception_handler import APIError
from apps.common.api_responses.constants import (
    ERROR_INVALID_CREDENTIALS,
    ERROR_USER_ACCOUNT_INACTIVE,
    ERROR_INVALID_EXPIRED_REFRESH_TOKEN
)
from apps.common.audit.services import log_audit_event
from .models import User


def authenticate_and_generate_tokens(email, password, role=None):
    """
    Authenticate user and generate JWT tokens
    
    Args:
        email (str): User email
        password (str): User password  
        role (str): User role
        
    Returns:
        dict: Contains access_token, refresh_token, expires_in and user data
        
    Raises:
        APIError: For authentication failures
    """
    # Use Django's authenticate to validate credentials via configured auth backends
    user = authenticate(None, email=email, password=password)
    if user is None:
        raise APIError(ERROR_INVALID_CREDENTIALS)

    # Check if user is active
    if not user.is_active:
        raise APIError(ERROR_USER_ACCOUNT_INACTIVE)

    # Check if user has groups assigned (role validation)
    # if not user.groups.exists():
    #     raise APIError(ERROR_INVALID_CREDENTIALS)
    
    # Generate tokens
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    
    # Calculate expires_in using token claims
    expires_in = access_token['exp'] - access_token['iat']
    
    return {
        'access_token': str(access_token),
        'refresh_token': str(refresh),
        'expires_in': expires_in,
        'user': {
            'user_id': str(user.id),
            'email': user.email,
            'role': user.role  
        }
    }


def get_access_token(refresh_token_str):
    """
    Generate new access token from refresh token
    
    Args:
        refresh_token_str (str): Refresh token string
        
    Returns:
        dict: Contains new access_token and expires_in
        
    Raises:
        APIError: For invalid or expired refresh tokens
    """
    try:
        refresh_token = RefreshToken(refresh_token_str)
        access_token = refresh_token.access_token
        
        # Calculate expires_in using token claims
        expires_in = access_token['exp'] - access_token['iat']
        
        return {
            'access_token': str(access_token),
            'expires_in': expires_in
        }
    except (TokenError, InvalidToken):
        raise APIError(ERROR_INVALID_EXPIRED_REFRESH_TOKEN)


def generate_password_reset_token(user):
    """
    Generate password reset token and uidb64
    
    Args:
        user (User): User instance
        
    Returns:
        tuple: (token, uidb64)
    """
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    return token, uidb64


def validate_password_reset_token(token, uidb64):
    """
    Validate password reset token and return user
    
    Args:
        token (str): Reset token
        uidb64 (str): Base64 encoded user ID
        
    Returns:
        User: User instance if valid
        
    Raises:
        APIError: For invalid tokens
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        raise APIError(ERROR_INVALID_CREDENTIALS)
    
    if not user.is_active:
        raise APIError(ERROR_USER_ACCOUNT_INACTIVE)
    
    if not default_token_generator.check_token(user, token):
        raise APIError(ERROR_INVALID_CREDENTIALS)
    
    return user
