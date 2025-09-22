from django.urls import path
from .views import (
    LoginView,
    RefreshTokenView,
    LogoutView,
    UserRegistrationView,
    WhoamiView,
    ForgotPasswordView,
    ResetPasswordView,
    ChangePasswordView
)

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh_token'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/whoami/', WhoamiView.as_view(), name='whoami'),
    path('auth/register/', UserRegistrationView.as_view(), name='register'),

    # Password management endpoints
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]