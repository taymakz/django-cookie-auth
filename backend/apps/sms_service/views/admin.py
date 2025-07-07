from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.telegram_service.utils.messages.main import (
    telegram_service_admin_group_message,
    TGServiceAdminTOPICS,
)
from apps.sms_service.models import VerifyOTPService


class OTPResultView(APIView):
    """
    API view to receive OTP result notifications and send Telegram alerts.
    """

    authentication_classes = []  # No authentication required for this endpoint

    def post(self, request):
        """
        Handle POST requests with OTP result data.
        Expected payload:
        {
            "phone": "string",
            "code": "string",
            "status": "success" | "failed",
            "error": "string" (optional, for failed status),
            "result": "string" (optional, for additional data)
        }
        """
        try:
            data = request.data
            phone = data.get("phone")
            code = data.get("code")
            result_status = data.get("status")
            error = data.get("error", "")
            result_data = data.get("result", "")

            if not phone or not code or not result_status:
                return Response(
                    {"error": "Missing required fields: phone, code, status"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Find the OTP record
            otp_record = VerifyOTPService.get_by_phone_and_code(phone, code)

            if result_status == "success":
                # Update OTP record if found
                if otp_record:
                    otp_record.mark_as_sent_success(result_data)

                # Send success notification to SMS alerts
                success_message = (
                    "✅ SMS ارسال شد\n\n"
                    f"شماره: {phone}\n"
                    f"کد: {code}\n"
                    f"وضعیت: موفق"
                )
                if result_data:
                    success_message += f"\nنتیجه: {result_data}"

                telegram_service_admin_group_message(
                    topic=TGServiceAdminTOPICS.SMS_ALERTS,
                    message=success_message,
                )
            elif result_status == "failed":
                # Update OTP record if found
                if otp_record:
                    otp_record.mark_as_sent_failed(error)

                # Send failure notification to SMS alerts
                error_message = (
                    "❌ خطا در ارسال SMS\n\n"
                    f"شماره: {phone}\n"
                    f"کد: {code}\n"
                    f"خطا: {error}\n"
                    f"وضعیت: ناموفق"
                )
                telegram_service_admin_group_message(
                    topic=TGServiceAdminTOPICS.SMS_ALERTS,
                    message=error_message,
                )
            else:
                return Response(
                    {"error": "Invalid status. Must be 'success' or 'failed'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "message": "OTP result processed successfully",
                    "otp_found": otp_record is not None,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # Send error notification
            error_message = (
                "🚨 خطا در پردازش نتیجه SMS\n\n"
                f"خطا: {str(e)}\n"
                f"درخواست: {request.data}"
            )
            telegram_service_admin_group_message(
                topic=TGServiceAdminTOPICS.ERRORS,
                message=error_message,
            )

            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ClearUsedOTPView(APIView):
    """
    API view to clear all used OTP objects.
    """

    authentication_classes = []  # No authentication required for this endpoint

    def delete(self, request):
        """
        Delete all used OTP records.
        """
        try:

            # Delete all used OTP records
            deleted_count, _ = VerifyOTPService.objects.filter(is_used=True).delete()

            # Send notification to admin
            admin_message = (
                "🗑️ پاکسازی OTP های استفاده شده\n\n"
                f"تعداد حذف شده: {deleted_count}\n"
                f"وضعیت: موفق"
            )
            telegram_service_admin_group_message(
                topic=TGServiceAdminTOPICS.SMS_ALERTS,
                message=admin_message,
            )

            return Response(
                {
                    "ok": "true",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # Send error notification
            error_message = "🚨 خطا در پاکسازی OTP ها\n\n" f"خطا: {str(e)}"
            telegram_service_admin_group_message(
                topic=TGServiceAdminTOPICS.ERRORS,
                message=error_message,
            )

            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
