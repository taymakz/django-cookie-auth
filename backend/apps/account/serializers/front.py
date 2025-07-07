from rest_framework import serializers

from apps.account.models import User
from config.libs.validators import validate_phone
import uuid


class AcountCurrentUserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the current user's account details.
    """

    has_password = serializers.BooleanField(source="has_usable_password")

    class Meta:
        model = User
        fields = (
            "phone",
            "first_name",
            "last_name",
            "has_password",
        )


class AccountUserLogoutSerializer(serializers.Serializer):
    """
    Serializer for logging out the user.
    """

    refresh = serializers.CharField()


class BasePhoneValidationSerializer(serializers.Serializer):
    """
    Base serializer for phone validation.
    """

    phone = serializers.CharField(max_length=11, min_length=10)

    def validate_phone(self, value):
        validated_phone = validate_phone(value)
        if not validated_phone:
            raise serializers.ValidationError("Invalid phone number format.")
        return User.format_phone(value)


class AccountUserAuthenticateCheckSerializer(BasePhoneValidationSerializer):
    """
    Serializer to check user Authenticate info (Already exist or not).
    BasePhoneValidationSerializer is used to validate the phone number format.
    """

    pass


class AccountUserAuthenticatePasswordSerialzer(BasePhoneValidationSerializer):
    """
    Serializer for user authentication with phone and password.
    BasePhoneValidationSerializer is used to validate the phone number format.

    """

    password = serializers.CharField(min_length=8, max_length=32)


class AccountUserAuthenticateOTPSerialzer(BasePhoneValidationSerializer):
    """
    Serializer for user authentication with phone and otp.
    BasePhoneValidationSerializer is used to validate the phone number format.

    """

    otp = serializers.CharField(max_length=4, min_length=4)
    referral_code = serializers.CharField(
        max_length=6, min_length=6, required=False, allow_blank=True
    )


class AccountUserAuthenticateResetPasswordCheckSerialzer(BasePhoneValidationSerializer):
    """
    Serializer to check user Authenticate info for resetting password (Already exist or not).
    BasePhoneValidationSerializer is used to validate the phone number format.

    """

    pass


class AccountUserAuthenticateResetPasswordOTPSerialzer(BasePhoneValidationSerializer):
    """
    Serializer for user authentication with phone and otp for resetting password.
    BasePhoneValidationSerializer is used to validate the phone number format.

    """

    otp = serializers.CharField(max_length=4, min_length=4)


class AccountUserAuthenticateResetPasswordSerialzer(BasePhoneValidationSerializer):
    """
    Serializer for resetting user password with phone, token, and new password.
    BasePhoneValidationSerializer is used to validate the phone number format.
    """

    token = serializers.CharField()
    password = serializers.CharField(min_length=8, max_length=32)
    confirm_password = serializers.CharField(min_length=8, max_length=32)

    def validate(self, attrs):
        """
        Validate that the password and confirm_password match.
        """
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError("Passwords do not match.")
        return attrs


class AuthenticateUserForgotPasswordCheckSerializer(BasePhoneValidationSerializer):
    """
    Serializer to check user authentication for forgot password flow.
    BasePhoneValidationSerializer is used to validate the phone number format.
    """

    pass


class AuthenticateUserForgotPasswordOTPSerializer(BasePhoneValidationSerializer):
    """
    Serializer for user authentication with phone and OTP for forgot password flow.
    BasePhoneValidationSerializer is used to validate the phone number format.
    """

    otp = serializers.CharField(max_length=4, min_length=4)


class AuthenticateUserForgotPasswordResetSerializer(BasePhoneValidationSerializer):
    """
    Serializer for resetting user password in forgot password flow.
    BasePhoneValidationSerializer is used to validate the phone number format.
    """

    token = serializers.CharField()
    password = serializers.CharField(min_length=8, max_length=32)
    confirm_password = serializers.CharField(min_length=8, max_length=32)

    def validate_token(self, value):
        """
        Validate that the token is in UUID4 format.
        """
        try:
            uuid_obj = uuid.UUID(value, version=4)
            if str(uuid_obj) != value:
                raise ValueError
        except ValueError:
            raise serializers.ValidationError("Token must be a valid UUID4 format.")
        return value

    def validate(self, attrs):
        """
        Validate that the password and confirm_password match.
        """
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
