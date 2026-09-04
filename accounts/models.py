"""User and OTP models."""
from __future__ import annotations

import datetime as dt
import hashlib

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

from common.enums import OTPPurpose, UserRole
from common.models import BaseModel
from common.storages import image_storage
from common.validators import validate_full_name, validate_image_upload, validate_phone_number


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.full_clean(exclude=["password"])
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra):
        extra.setdefault("role", UserRole.USER)
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email: str, password: str | None = None, **extra):
        extra.setdefault("role", UserRole.ADMIN)
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_verified", True)
        extra.setdefault("is_active", True)
        extra.setdefault("full_name", "Administrator")
        if extra.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        return self._create_user(email, password, **extra)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    """Custom user identified by email."""

    full_name = models.CharField(max_length=100, validators=[validate_full_name])
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(
        max_length=20, unique=True, db_index=True, validators=[validate_phone_number]
    )
    profile_image = models.ImageField(
        upload_to="profiles/", storage=image_storage, validators=[validate_image_upload],
        blank=True, null=True,
    )
    role = models.CharField(
        max_length=10, choices=UserRole.choices, default=UserRole.USER, db_index=True
    )
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "phone_number"]

    class Meta:
        db_table = "accounts_user"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["role", "is_active"])]

    def __str__(self) -> str:
        return f"{self.full_name} <{self.email}>"

    def save(self, *args, **kwargs):
        self.email = self.email.lower().strip()
        if self.role == UserRole.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN


def hash_otp(code: str) -> str:
    """OTPs are never stored in plaintext."""
    salt = settings.SECRET_KEY
    return hashlib.sha256(f"{salt}:{code}".encode()).hexdigest()


class OTPQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_used=False, expires_at__gt=timezone.now())


class OTP(BaseModel):
    """One-time password with purpose, expiry and single-use semantics."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    code_hash = models.CharField(max_length=64)
    purpose = models.CharField(max_length=20, choices=OTPPurpose.choices, db_index=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(blank=True, null=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    is_verified = models.BooleanField(default=False)  # verified but not yet consumed

    objects = OTPQuerySet.as_manager()

    class Meta:
        db_table = "accounts_otp"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "purpose", "is_used"])]

    def __str__(self) -> str:
        return f"OTP({self.user.email}, {self.purpose})"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    def matches(self, code: str) -> bool:
        return self.code_hash == hash_otp(code)

    def consume(self) -> None:
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=["is_used", "used_at", "updated_at"])

    @staticmethod
    def default_expiry() -> dt.datetime:
        return timezone.now() + dt.timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
