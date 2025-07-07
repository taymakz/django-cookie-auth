from datetime import timedelta
from random import randint
from django.db import models
from django.utils.timezone import now


class VerifyOTPService(models.Model):
    """
    Model to handle OTP (One-Time Password) verification services.

    Attributes:
        usage: Indicates the purpose of the OTP (e.g., AUTHENTICATE, RESET_PASSWORD, VERIFY).
        to: The recipient's phone number or email address.
        code: The OTP code sent to the recipient.
        is_sent: Boolean indicating if the OTP has been sent.
        send_status: Status of the sending operation (PENDING, SUCCESS, FAILED).
        is_used: Boolean indicating if the OTP has been used.
        result: Stores the result of the OTP sending operation.
        error_message: Stores error details if sending failed.
        expire_at: The date and time when the OTP expires.
        created_at: When the OTP was created.
        sent_at: When the OTP was sent (if successful).
    """

    class VerifyOTPServiceUsageChoice(models.TextChoices):
        AUTHENTICATE = "AUTHENTICATE", "Authenticate"
        RESET_PASSWORD = "RESET_PASSWORD", "Reset Password"
        VERIFY = "VERIFY", "Verify"

    class SendStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    usage = models.CharField(
        max_length=17,
        choices=VerifyOTPServiceUsageChoice,
        default=VerifyOTPServiceUsageChoice.AUTHENTICATE,
    )
    to = models.CharField(max_length=355)
    code = models.CharField(max_length=5)
    is_sent = models.BooleanField(default=False)
    send_status = models.CharField(
        max_length=10,
        choices=SendStatus.choices,
        default=SendStatus.PENDING,
    )
    is_used = models.BooleanField(default=False)
    result = models.TextField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    expire_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "sms_service_verify_otp"

    def __str__(self):
        return f"{self.to} : {self.code}"

    def save(self, *args, **kwargs):
        """
        Overrides the save method to automatically generate an OTP code and expiration time
        if the record is being created.
        """
        if not self.pk:
            self.code = str(randint(1000, 9999))
            self.expire_at = now() + timedelta(seconds=240)
        super().save(*args, **kwargs)

    def is_expired(self):
        return self.expire_at < now()

    def mark_as_sent_success(self, result_data=None):
        """Mark OTP as successfully sent."""
        self.is_sent = True
        self.send_status = self.SendStatus.SUCCESS
        self.sent_at = now()
        if result_data:
            self.result = str(result_data)
        self.save(update_fields=["is_sent", "send_status", "sent_at", "result"])

    def mark_as_sent_failed(self, error_message=None):
        """Mark OTP as failed to send."""
        self.is_sent = False
        self.send_status = self.SendStatus.FAILED
        if error_message:
            self.error_message = str(error_message)
        self.save(update_fields=["is_sent", "send_status", "error_message"])

    def send_otp(self):
        """Send OTP if not expired."""
        if not self.is_expired():
            from apps.sms_service.utils.otp import sms_service_send_otp
            print(f"One Time Code: {self.code}")
            # Todo uncomment
            # return sms_service_send_otp(self.to, self.code)
        return False

    @classmethod
    def get_by_phone_and_code(cls, phone, code):
        """Get OTP record by phone and code."""
        try:
            return cls.objects.get(to=phone, code=code, is_used=False)
        except cls.DoesNotExist:
            return None
