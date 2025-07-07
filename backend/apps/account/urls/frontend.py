from django.urls import path

from apps.account.views import frontend
from config.api.jwt import CustomTokenRefreshView

app_name = "account_frontend"

urlpatterns = [
    path(
        "authenticate/token-refresh/",
        CustomTokenRefreshView.as_view(),
        name="account_user_token_refresh",
    ),
    path(
        "authenticate/current/",
        frontend.AccountUserCurrentDetailView.as_view(),
        name="account_user_current_detail",
    ),
    # Endpoint for checking user authentication
    path(
        "authenticate/check/",
        frontend.AccountUserAuthenticationCheckView.as_view(),
        name="account_user_authentication_check",
    ),
    # Endpoint for password-based user authentication
    path(
        "authenticate/password/",
        frontend.AccountUserAuthenticatePasswordView.as_view(),
        name="account_user_authentication_password",
    ),
    # Endpoint for OTP-based user authentication
    path(
        "authenticate/otp/",
        frontend.AccountUserAuthenticateOTPView.as_view(),
        name="account_user_authentication_otp",
    ),
    path(
        "authenticate/logout/",
        frontend.AccountUserLogoutView.as_view(),
        name="account_user_logout",
    ),
    # Endpoints for user forget password flow
    path(
        "authenticate/forget-password/check/",
        frontend.AccountUserForgotPasswordCheckView.as_view(),
        name="account_user_forget_password_check",
    ),
    path(
        "authenticate/forget-password/otp/",
        frontend.AccountUserForgetPasswordOTPView.as_view(),
        name="account_user_forget_password_otp",
    ),
    path(
        "authenticate/forget-password/reset/",
        frontend.AccountUserForgetPasswordResetView.as_view(),
        name="account_user_forget_password_reset",
    ),
]
