from django.urls import path
from apps.sms_service.views import admin

urlpatterns = [
    path("result/otp/", admin.OTPResultView.as_view(), name="otp-result"),
    path("clear/used-otp/", admin.ClearUsedOTPView.as_view(), name="clear-used-otp"),
]
