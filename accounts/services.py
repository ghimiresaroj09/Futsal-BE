"""Authentication and OTP business logic (kept out of views)."""
from __future__ import annotations

import datetime as dt
import logging

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import OTP, User, hash_otp
from common.enums import OTPPurpose
from common.exceptions import RateLimitedError, ServiceError
from common.utils import generate_numeric_code
from notifications.emails import send_otp_email

logger = logging.getLogger("futsal.auth")


# --------------------------------------------------------------------- OTP
def _enforce_otp_rate_limit(user: User, purpose: str) -> None:
    now = timezone.now()
    window_start = now - dt.timedelta(hours=1)
    recent = OTP.objects.filter(user=user, purpose=purpose, created_at__gte=window_start)
    if recent.count() >= settings.OTP_MAX_PER_HOUR:
        raise RateLimitedError("Too many OTP requests. Please try again later.")
    last = recent.order_by("-created_at").first()
    if last and (now - last.created_at).total_seconds() < settings.OTP_RESEND_COOLDOWN_SECONDS:
        raise RateLimitedError(
            f"Please wait {settings.OTP_RESEND_COOLDOWN_SECONDS} seconds before requesting a new OTP."
        )


@transaction.atomic
def issue_otp(*, user: User, purpose: str, enforce_rate_limit: bool = True) -> OTP:
    """Invalidate previous OTPs for the purpose, create and email a fresh one."""
    if enforce_rate_limit:
        _enforce_otp_rate_limit(user, purpose)

    OTP.objects.filter(user=user, purpose=purpose, is_used=False).update(
        is_used=True, used_at=timezone.now()
    )
    code = generate_numeric_code(6)
    otp = OTP.objects.create(
        user=user,
        code_hash=hash_otp(code),
        purpose=purpose,
        expires_at=OTP.default_expiry(),
    )
    transaction.on_commit(
        lambda: send_otp_email(
            email=user.email,
            full_name=user.full_name,
            code=code,
            purpose=purpose,
            expiry_minutes=settings.OTP_EXPIRY_MINUTES,
        )
    )
    logger.info("OTP issued user=%s purpose=%s", user.id, purpose)
    return otp


def verify_otp(*, user: User, code: str, purpose: str, consume: bool = True) -> OTP:
    """Validate an OTP. Raises ServiceError on any failure."""
    otp = (
        OTP.objects.filter(user=user, purpose=purpose, is_used=False)
        .order_by("-created_at")
        .first()
    )
    if otp is None:
        raise ServiceError("No active OTP found. Please request a new one.",
                           errors={"otp": ["No active OTP found."]})
    if otp.is_expired:
        otp.consume()
        raise ServiceError("OTP has expired. Please request a new one.",
                           errors={"otp": ["OTP has expired."]})
    if otp.attempts >= settings.OTP_MAX_ATTEMPTS:
        otp.consume()
        raise RateLimitedError("Too many invalid attempts. Please request a new OTP.")
    if not otp.matches(code):
        otp.attempts += 1
        otp.save(update_fields=["attempts", "updated_at"])
        logger.warning("Invalid OTP attempt user=%s purpose=%s", user.id, purpose)
        raise ServiceError("Invalid OTP.", errors={"otp": ["Invalid OTP."]})

    otp.is_verified = True
    if consume:
        otp.is_used = True
        otp.used_at = timezone.now()
    otp.save(update_fields=["is_verified", "is_used", "used_at", "updated_at"])
    return otp


# ------------------------------------------------------------- registration
@transaction.atomic
def register_user(*, full_name: str, email: str, phone_number: str, password: str) -> User:
    user = User.objects.create_user(
        email=email,
        password=password,
        full_name=full_name.strip(),
        phone_number=phone_number,
        is_verified=False,
        is_active=True,
    )
    issue_otp(user=user, purpose=OTPPurpose.REGISTRATION, enforce_rate_limit=False)
    logger.info("User registered id=%s", user.id)
    return user


def activate_user(user: User) -> User:
    user.is_verified = True
    user.is_active = True
    user.save(update_fields=["is_verified", "is_active", "updated_at"])
    logger.info("User verified id=%s", user.id)
    return user


# -------------------------------------------------------------------- auth
def issue_tokens(user: User) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


def login_user(*, email: str, password: str) -> tuple[User, dict[str, str]]:
    user = authenticate(username=email.lower().strip(), password=password)
    if user is None:
        logger.warning("Failed login attempt for email=%s", email)
        raise ServiceError("Invalid email or password.",
                           errors={"detail": ["Invalid email or password."]})
    if not user.is_verified:
        raise ServiceError(
            "Account is not verified. Please verify the OTP sent to your email.",
            errors={"detail": ["Account not verified."]},
        )
    if not user.is_active:
        raise ServiceError("Account is disabled.", errors={"detail": ["Account is disabled."]})
    return user, issue_tokens(user)


def blacklist_all_user_tokens(user: User) -> None:
    """Invalidate every outstanding refresh token for the user."""
    from rest_framework_simplejwt.token_blacklist.models import (
        BlacklistedToken, OutstandingToken,
    )

    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)


def change_password(*, user: User, old_password: str, new_password: str) -> None:
    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])
    blacklist_all_user_tokens(user)
    logger.info("Password changed user=%s", user.id)


def reset_password(*, user: User, new_password: str) -> None:
    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])
    blacklist_all_user_tokens(user)
    logger.info("Password reset user=%s", user.id)
