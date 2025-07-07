from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from typing import Any

from apps.account.models import User
from apps.account.serializers.front import (
    AcountCurrentUserDetailSerializer,
    AccountUserLogoutSerializer,
    AccountUserAuthenticateCheckSerializer,
    AccountUserAuthenticateOTPSerialzer,
    AccountUserAuthenticatePasswordSerialzer,
    AuthenticateUserForgotPasswordCheckSerializer,
    AuthenticateUserForgotPasswordOTPSerializer,
    AuthenticateUserForgotPasswordResetSerializer,
)
from apps.account.enums import AccountUserAuthenticateCheckSectionEnum
from config.api.enums import ResponseMessage
from config.api.response import BaseResponse, JWTCookieResponse, clear_jwt_cookies
from config.api.authentication import JWTCookieAuthentication
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.sms_service.models import VerifyOTPService


class AccountUserCurrentDetailView(RetrieveAPIView):
    """
    View to retrieve the current user's account details.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AcountCurrentUserDetailSerializer

    def get_object(self) -> Any:
        return self.request.user

    def get_queryset(self) -> Any:
        return User.objects.select_related("subscription").all()

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.serializer_class(user)
        return BaseResponse(data=serializer.data, status=status.HTTP_200_OK)


class AccountUserLogoutView(APIView):
    """
    API endpoint for logging out a user by blacklisting their refresh token.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AccountUserLogoutSerializer

    def post(self, request):
        """
        Handle user logout by deleting the refresh token.
        """
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST, message=ResponseMessage.FAILED.value
            )

        try:
            refresh_token = request.data.get("refresh")
            # If no refresh token in request body, try to get it from cookies
            if not refresh_token:
                refresh_token = request.COOKIES.get("refresh_token")

            # Blacklist the refresh token using Django Rest Framework SimpleJWT
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception as _:
                    pass

            # Create response and clear JWT cookies
            response = BaseResponse(
                status=status.HTTP_200_OK,
                message=ResponseMessage.SUCCESS.value,
            )

            # Clear JWT cookies using utility function
            clear_jwt_cookies(response)

            return response
        except Exception as _:
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST, message=ResponseMessage.FAILED.value
            )


class AccountUserAuthenticationCheckView(APIView):
    """
    API endpoint to check if a user exists based on their phone number.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = AccountUserAuthenticateCheckSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST, message=ResponseMessage.FAILED.value
            )
        phone = serializer.validated_data.get("phone")  # type: ignore
        user = (
            User.objects.only(
                "id",
                "phone",
                "password",
            )
            .filter(phone=phone)
            .first()
        )

        # Check for the latest OTP service record for phone authentication
        otp_service = (
            VerifyOTPService.objects.only(
                "id", "usage", "to", "code", "expire_at", "is_used"
            )
            .filter(
                to=phone,
                usage=VerifyOTPService.VerifyOTPServiceUsageChoice.AUTHENTICATE,
                is_used=False,
            )
            .order_by("-id")
            .first()
        )

        # If user doesn't exist, send OTP for registration
        if not user:
            # Send OTP using SMS service
            if not otp_service or otp_service.is_expired():
                otp_service = VerifyOTPService.objects.create(
                    to=phone,
                    usage=VerifyOTPService.VerifyOTPServiceUsageChoice.AUTHENTICATE,
                )
                otp_service.send_otp()

            return BaseResponse(
                data={
                    "section": AccountUserAuthenticateCheckSectionEnum.OTP.value,
                },
                status=status.HTTP_200_OK,
                message=ResponseMessage.PHONE_OTP_SENT.value.format(phone=phone),
            )

        # If user exists and has a usable password, use password authentication
        if user.has_usable_password():
            return BaseResponse(
                data={
                    "section": AccountUserAuthenticateCheckSectionEnum.PASSWORD.value
                },
                status=status.HTTP_200_OK,
                message=ResponseMessage.SUCCESS.value,
            )
        if not otp_service or otp_service.is_expired():
            # If user exists but no password, send OTP
            otp_service = VerifyOTPService.objects.create(
                to=phone,
                usage=VerifyOTPService.VerifyOTPServiceUsageChoice.AUTHENTICATE,
            )
            otp_service.send_otp()

        return BaseResponse(
            data={
                "section": AccountUserAuthenticateCheckSectionEnum.OTP.value,
            },
            status=status.HTTP_200_OK,
            message=ResponseMessage.SUCCESS.value,
        )


class AccountUserAuthenticateOTPView(APIView):
    """
    API endpoint for authenticating a user with OTP.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = AccountUserAuthenticateOTPSerialzer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST, message=ResponseMessage.FAILED.value
            )

        phone = serializer.validated_data.get("phone")  # type: ignore
        otp = serializer.validated_data.get("otp")  # type: ignore
        referral_code = serializer.validated_data.get("referral_code")  # type: ignore

        # Verify OTP
        otp_service = (
            VerifyOTPService.objects.filter(
                to=phone,
                usage=VerifyOTPService.VerifyOTPServiceUsageChoice.AUTHENTICATE,
                code=otp,
            )
            .order_by("-id")
            .first()
        )

        if not otp_service or otp_service.is_expired():
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message=ResponseMessage.AUTH_WRONG_OTP.value,
            )

        # Get or create user
        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={
                "is_active": True,
                "referral_from": referral_code if referral_code else None,
            },
        )
        if created:
            user.handle_creation()


        # Mark OTP as used
        otp_service.is_used = True
        otp_service.save(update_fields=["is_used"])

        # Generate JWT tokens
        tokens = user.generate_jwt_token()

        return JWTCookieResponse(
            data=None,  # No tokens in response body
            jwt_tokens=tokens,
            status=status.HTTP_200_OK,
            message=ResponseMessage.AUTH_LOGIN_SUCCESSFULLY.value,
        )


class AccountUserAuthenticatePasswordView(APIView):
    """
    API endpoint for authenticating a user with password.
    """

    permission_classes = [AllowAny]
    serializer_class = AccountUserAuthenticatePasswordSerialzer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST, message=ResponseMessage.FAILED.value
            )

        phone = serializer.validated_data.get("phone")  # type: ignore
        password = serializer.validated_data.get("password")  # type: ignore

        # Get user
        user = User.objects.filter(phone=phone).first()
        if not user or not password:
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message=ResponseMessage.AUTH_WRONG_PASSWORD.value,
            )

        # Check password
        if not user.check_password(password):
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message=ResponseMessage.AUTH_WRONG_PASSWORD.value,
            )

        # Generate JWT tokens
        tokens = user.generate_jwt_token()

        return JWTCookieResponse(
            data=None,  # No tokens in response body
            jwt_tokens=tokens,
            status=status.HTTP_200_OK,
            message=ResponseMessage.AUTH_LOGIN_SUCCESSFULLY.value,
        )


class AccountUserForgotPasswordCheckView(APIView):
    """
    API endpoint to check user existence and send OTP for forgot password flow.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = AuthenticateUserForgotPasswordCheckSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST, message=ResponseMessage.FAILED.value
            )
        phone = serializer.validated_data.get("phone")  # type: ignore
        user = User.objects.filter(phone=phone).first()
        if not user:
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message="کاربری با این شماره پیدا نشد.",
            )
        otp_service, _ = VerifyOTPService.objects.get_or_create(
            to=phone,
            usage=VerifyOTPService.VerifyOTPServiceUsageChoice.RESET_PASSWORD,
        )
        if otp_service.is_expired():
            otp_service.delete()
            otp_service = VerifyOTPService.objects.create(
                to=phone,
                usage=VerifyOTPService.VerifyOTPServiceUsageChoice.RESET_PASSWORD,
            )
        otp_service.send_otp()
        return BaseResponse(
            status=status.HTTP_200_OK,
            message=ResponseMessage.PHONE_OTP_SENT.value.format(phone=phone),
        )


class AccountUserForgetPasswordOTPView(APIView):
    """
    API endpoint to validate OTP for forgot password flow and return reset token.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = AuthenticateUserForgotPasswordOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST, message=ResponseMessage.FAILED.value
            )
        phone = serializer.validated_data.get("phone")  # type: ignore
        otp = serializer.validated_data.get("otp")  # type: ignore
        user = User.objects.filter(phone=phone).first()
        if not user:
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message="کاربری با این شماره پیدا نشد.",
            )
        otp_service = (
            VerifyOTPService.objects.filter(
                to=phone,
                usage=VerifyOTPService.VerifyOTPServiceUsageChoice.RESET_PASSWORD,
                code=otp,
            )
            .order_by("-id")
            .first()
        )
        if not otp_service or otp_service.is_expired():
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message=ResponseMessage.AUTH_WRONG_OTP.value,
            )
        # حذف OTP بعد از استفاده
        otp_service.delete()
        # ساخت توکن ریست پسورد
        from apps.account.models import UserPasswordResetToken

        reset_token = UserPasswordResetToken.objects.create(user=user)
        return BaseResponse(
            data={"token": str(reset_token.token)},
            status=status.HTTP_200_OK,
        )


class AccountUserForgetPasswordResetView(APIView):
    """
    API endpoint to reset password using phone, token, and new password.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = AuthenticateUserForgotPasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST, message=ResponseMessage.FAILED.value
            )
        phone = serializer.validated_data.get("phone")  # type: ignore
        token = serializer.validated_data.get("token")  # type: ignore
        password = serializer.validated_data.get("password")  # type: ignore
        confirm_password = serializer.validated_data.get("confirm_password")  # type: ignore
        user = User.objects.filter(phone=phone).first()
        if not user:
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST, message=ResponseMessage.FAILED.value
            )
        from apps.account.models import UserPasswordResetToken

        try:
            reset_token = UserPasswordResetToken.objects.get(user=user, token=token)
        except UserPasswordResetToken.DoesNotExist:
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST, message=ResponseMessage.FAILED.value
            )
        if reset_token.is_expired():
            reset_token.delete()
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST, message="توکن منقضی شده است."
            )
        # اعتبارسنجی رمز عبور
        from config.libs.validators import validate_password

        is_valid, msg = validate_password(password)
        if not is_valid:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST, message=msg)
        if password != confirm_password:
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST,
                message=ResponseMessage.PASSWORDS_DO_NOT_MATCH.value,
            )
        user.set_password(password)
        user.save()
        reset_token.delete()
        return BaseResponse(
            status=status.HTTP_200_OK,
            message="رمز عبور با موفقیت تغییر کرد.",
        )
