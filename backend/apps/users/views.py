from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction
from decouple import config
from apps.common.api_responses.responses import success_response
from apps.common.api_responses.constants import (
    SUCCESS_USER_LOGIN, SUCCESS_ACCESS_TOKEN_RETRIEVED, SUCCESS_LOGOUT,
    SUCCESS_USER_REGISTERED, SUCCESS_USER_INFO_FETCHED,
    SUCCESS_PASSWORD_RESET_EMAIL_SENT, SUCCESS_PASSWORD_RESET, SUCCESS_PASSWORD_CHANGED,
    ERROR_INVALID_CREDENTIALS
)
from apps.common.api_responses.exception_handler import APIError
from apps.common.email.tasks import send_email_task

from .models import User
from .serializers import (
    LoginSerializer, RefreshTokenSerializer,
    UserRegistrationSerializer, ForgotPasswordSerializer,
    ResetPasswordSerializer, ChangePasswordSerializer
)
from .services import (
    authenticate_and_generate_tokens, get_access_token,
    generate_password_reset_token, validate_password_reset_token
)


class LoginView(APIView):
    """
    Handles user authentication and JWT token generation.
    
    Supports login for different user roles (csr, government, sdgcc, planning, super_admin)
    with role mapping between frontend and backend roles.
    
    POST /api/auth/login/
    Request: {"data": {"email": "user@example.com", "password": "password", "role": "csr"}}
    Response: JWT tokens with user data
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data.get('data', {}))
        serializer.is_valid(raise_exception=True)
        
        token_data = authenticate_and_generate_tokens(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        return success_response(
            message_code=SUCCESS_USER_LOGIN,
            data=token_data
        )


class RefreshTokenView(APIView):
    """
    Generates new access token from valid refresh token.
    
    POST /api/auth/refresh/
    Request: {"data": {"refresh_token": "refresh_token_string"}}
    Response: New access token with expiry information
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data.get('data', {}))
        serializer.is_valid(raise_exception=True)
        
        token_data = get_access_token(serializer.validated_data['refresh_token'])
        
        return success_response(
            message_code=SUCCESS_ACCESS_TOKEN_RETRIEVED,
            data=token_data
        )


class LogoutView(APIView):
    """
    Handles user logout.
    
    Simply returns success response as JWT tokens are stateless.
    Token invalidation happens on the client side.
    
    POST /api/auth/logout/
    Requires: Valid JWT token in Authorization header
    """
    
    def post(self, request):
        return success_response(message_code=SUCCESS_LOGOUT)


class UserRegistrationView(APIView):
    """
    Handles basic user registration.

    Creates User record with basic information.

    POST /api/auth/register/
    Request: {"data": {"email": "user@example.com", "password": "password", "full_name": "User Name", "contact_number": "1234567890"}}
    Response: Created user data
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data.get('data', {}))
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # Create User object
            user = User.objects.create_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                full_name=serializer.validated_data['full_name'],
                contact_number=serializer.validated_data.get('contact_number', '')
            )

            # Check environment variable for auto-approval
            # auto_approve = config('AUTO_APPROVE_USERS', default=True, cast=bool)
            # if auto_approve:
            #     from django.utils import timezone
            #     user.review_status = 'reviewed'
            #     user.reviewed_at = timezone.now()
            #     user.save()

            # Assign user to default user group
            # user.set_role('user')

            response_data = {
                'user': {
                    'id': str(user.id),
                    'full_name': user.full_name,
                    'email': user.email,
                    'contact_number': user.contact_number,
                    'role': user.role,
                    'created_at': user.created_at.isoformat()
                }
            }

            return success_response(
                message_code=SUCCESS_USER_REGISTERED,
                data=response_data
            )


class WhoamiView(APIView):
    """
    Returns current authenticated user information.

    GET /api/auth/whoami/
    Requires: Valid JWT token in Authorization header
    Response: User data
    """

    def get(self, request):
        user = request.user

        user_data = {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'contact_number': user.contact_number,
            # 'review_status': user.review_status,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat()
        }

        return success_response(
            message_code=SUCCESS_USER_INFO_FETCHED,
            data={'user': user_data}
        )


class ForgotPasswordView(APIView):
    """
    Initiates password reset process by sending reset email.
    
    Always returns success response for security reasons, even if
    the email doesn't exist in the system.
    
    POST /api/forgot-password/
    Request: {"data": {"email": "user@example.com"}}
    Response: Generic success message
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data.get('data', {}))
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                token, uidb64 = generate_password_reset_token(user)
                
                # Get frontend domain from environment
                frontend_domain = config('FRONTEND_DOMAIN', default='http://localhost:5173')
                reset_link = f"{frontend_domain}/reset-password?token={token}&uidb64={uidb64}"
                
                # Send password reset email using template
                send_email_task.delay(
                    subject="Password Reset Request - CSR Matchmaking",
                    recipient_list=[email],
                    template_name='emails/reset_password.html',
                    context={
                        'user_name': user.full_name,
                        'reset_link': reset_link
                    }
                )
        except User.DoesNotExist:
            pass  # Always return success for security
        
        return success_response(message_code=SUCCESS_PASSWORD_RESET_EMAIL_SENT)


class ResetPasswordView(APIView):
    """
    Completes password reset using token and uidb64 from email.
    
    Validates the reset token and updates user password if valid.
    Tokens have a 15-minute expiry configured in settings.
    
    POST /api/reset-password/
    Request: {"data": {"token": "reset_token", "uidb64": "encoded_user_id", "new_password": "newpass"}}
    Response: Success or error message
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data.get('data', {}))
        serializer.is_valid(raise_exception=True)
        
        user = validate_password_reset_token(
            serializer.validated_data['token'],
            serializer.validated_data['uidb64']
        )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return success_response(message_code=SUCCESS_PASSWORD_RESET)


class ChangePasswordView(APIView):
    """
    Allows authenticated users to change their password.
    
    Requires current password verification before allowing
    the password change for security.
    
    POST /api/change-password/
    Requires: Valid JWT token in Authorization header
    Request: {"data": {"old_password": "current", "new_password": "new"}}
    Response: Success or error message
    """
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data.get('data', {}))
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        if not user.check_password(serializer.validated_data['old_password']):
            raise APIError(ERROR_INVALID_CREDENTIALS)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return success_response(message_code=SUCCESS_PASSWORD_CHANGED)


