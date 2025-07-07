from typing import Dict, TYPE_CHECKING
from uuid import uuid4
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.timezone import now
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from datetime import timedelta
import random
import string

from config.libs.validators import validate_phone


class UserManager(BaseUserManager):
    """
    Custom user manager for User model.
    """

    def create_user(self, phone, **extra_fields):
        """
        Create and return a regular user with the given phone number.
        Password is set to unusable for normal users.
        """
        if not phone:
            raise ValueError("The Phone field must be set")

        # Set default values
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)

        user = self.model(phone=phone, **extra_fields)
        user.set_unusable_password()  # No password for normal users
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        """
        Create and return a superuser with the given phone number and password.
        """
        if not phone:
            raise ValueError("The Phone field must be set")
        if not password:
            raise ValueError("The Password field must be set for admin users")

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    phone = models.CharField(unique=True, max_length=11, db_index=True)
    referral_code = models.CharField(
        max_length=6, unique=True, null=True, blank=True, db_index=True
    )
    referral_from = models.CharField(max_length=6, null=True, blank=True, db_index=True)
    first_name = models.CharField(max_length=255, db_index=True)
    last_name = models.CharField(max_length=255, db_index=True)
    last_online = models.DateTimeField(null=True, blank=True)
    is_banned = models.BooleanField(default=False)
    banned_reason = models.CharField(max_length=255, null=True, blank=True)
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []  # no extra fields required for createsuperuser
    username = None
    email = None
    objects = UserManager()  # type: ignore

    class Meta:
        db_table = "users"

    def save(self, *args, **kwargs):
        # Generate referral code if it doesn't exist
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
        super().save(*args, **kwargs)

    def handle_creation(self):
        """
        Handles additional actions after user creation.
        This method is called after the user instance is created.
        """
        self.set_unusable_password()
        self.save(update_fields=["password"])

    def generate_referral_code(self) -> str:
        """
        Generates a unique 6-digit referral code using lowercase, uppercase letters and digits.
        """
        characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
        while True:
            code = "".join(random.choices(characters, k=6))
            # Check if this code already exists
            if not User.objects.filter(referral_code=code).exists():
                return code

    def generate_jwt_token(self) -> Dict[str, str | int]:
        """
        Generates JWT tokens (refresh and access) for the user.
        """
        refresh = RefreshToken.for_user(self)
        # Create custom access token with 5-minute expiry
        access = AccessToken.for_user(self)

        return {
            "refresh": str(refresh),
            "access": str(access),
            "access_exp": int(access.payload.get("exp") or 0),
        }

    @staticmethod
    def format_phone(phone: str) -> str:
        """
        Formats the phone number to ensure it is 11 digits long.
        If the phone number is less than 11 digits, it prepends '0'.
        If the phone number is already 11 digits, it returns it as is.
        """
        return phone if len(phone) == 11 else f"0{phone}"

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        validates the phone number.
        """
        return validate_phone(phone)



class UserPasswordResetToken(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reset_password_tokens"
    )
    token = models.UUIDField(editable=False, unique=True, blank=True, null=True)

    expire_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "users_password_reset_tokens"

    def __str__(self) -> str:
        return f"user : {self.user.username} - ({self.token})"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.token = uuid4()
            self.expire_at = now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def is_expired(self) -> bool:
        if self.expire_at:
            return self.expire_at < now()
        return True
