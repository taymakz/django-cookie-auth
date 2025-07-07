from django.urls import path

from apps.sms_service.views import front

app_name = "sms_service_front"

urlpatterns = [
    path(
        "request/otp/",
        front.VerificationRequestOTPView.as_view(),
        name="sms_service_request_otp",
    ),
]
