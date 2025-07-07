from rest_framework import serializers

from apps.account.serializers.front import BasePhoneValidationSerializer


class VerificationRequestOTPSerializer(BasePhoneValidationSerializer):
    """
    Serializer for requesting an OTP for phone verification.
    Inherits from BasePhoneValidationSerializer to validate phone number format.
    """
    otp_usage = serializers.CharField()
