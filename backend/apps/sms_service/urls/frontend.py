from django.urls import path

from sms_service.views import frontend

app_name = "sms_service_front"

urlpatterns = [
    path(
        "request/otp/",
        frontend.VerificationRequestOTPView.as_view(),
        name="sms_service_request_otp",
    ),
]
