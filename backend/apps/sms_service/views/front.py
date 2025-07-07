from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.account.models import User
from config.api.enums import ResponseMessage
from config.api.response import BaseResponse
from apps.sms_service.models import VerifyOTPService
from apps.sms_service.serializers.front import VerificationRequestOTPSerializer


class VerificationRequestOTPView(APIView):
    """
    API endpoint for requesting an OTP for verification.

    This view handles the generation and sending of OTPs for user verification.
    It supports both phone and email-based OTP requests.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = VerificationRequestOTPSerializer

    def post(self, request, _=None):
        serializer = self.serializer_class(data=request.data)

        # Validate the serializer data
        if not serializer.is_valid():
            return BaseResponse(
                status=status.HTTP_400_BAD_REQUEST, message=ResponseMessage.FAILED.value
            )

        phone = serializer.validated_data.get("phone")  # type: ignore
        otp_usage = serializer.validated_data.get("otp_usage")  # type: ignore

        # Check for existing OTP service record
        otp_service = (
            VerifyOTPService.objects.only(
                "id",
                "type",
                "to",
                "usage",
            )
            .filter(phone=phone, usage=otp_usage, is_used=False)
            .order_by("-id")
            .first()
        )
        # If OTP service exists and is not expired, return success
        if otp_service and not otp_service.is_expired():
            return BaseResponse(
                status=status.HTTP_200_OK,
                message=ResponseMessage.PHONE_OTP_SENT.value.format(phone=phone),
            )

        # If OTP service exists but is expired, delete it
        if otp_service and otp_service.is_expired():
            otp_service.delete()

        # Create a new OTP service and send the OTP
        new_otp_service = VerifyOTPService.objects.create(phone=phone, usage=otp_usage)
        new_otp_service.send_otp()

        return BaseResponse(
            status=status.HTTP_200_OK,
            message=ResponseMessage.PHONE_OTP_SENT.value.format(phone=phone),
        )
