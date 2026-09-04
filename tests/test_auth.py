"""Authentication flow tests."""
from __future__ import annotations

import datetime as dt

import pytest
from django.core import mail
from django.urls import reverse
from django.utils import timezone

from accounts.models import OTP, User, hash_otp
from accounts.services import issue_otp
from common.enums import OTPPurpose

pytestmark = pytest.mark.django_db

REGISTER_URL = "/api/v1/auth/register/"
VERIFY_URL = "/api/v1/auth/verify-otp/"
RESEND_URL = "/api/v1/auth/resend-otp/"
LOGIN_URL = "/api/v1/auth/login/"
REFRESH_URL = "/api/v1/auth/refresh/"
LOGOUT_URL = "/api/v1/auth/logout/"
CHANGE_PW_URL = "/api/v1/auth/change-password/"
FORGOT_URL = "/api/v1/auth/forgot-password/"
VERIFY_FORGOT_URL = "/api/v1/auth/verify-forgot-password-otp/"
RESET_URL = "/api/v1/auth/reset-password/"

PAYLOAD = {
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone_number": "9800000099",
    "password": "Strong@123",
    "confirm_password": "Strong@123",
}


def register(api, **overrides):
    return api.post(REGISTER_URL, {**PAYLOAD, **overrides}, format="json")


def set_known_otp(user, purpose=OTPPurpose.REGISTRATION, code="123456"):
    otp = OTP.objects.filter(user=user, purpose=purpose, is_used=False).latest("created_at")
    otp.code_hash = hash_otp(code)
    otp.save()
    return otp


def test_registration_creates_unverified_user_and_sends_otp(api, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        response = register(api)
    assert response.status_code == 201
    assert response.data["success"] is True
    user = User.objects.get(email="john@example.com")
    assert user.is_verified is False
    assert OTP.objects.filter(user=user, purpose=OTPPurpose.REGISTRATION).count() == 1
    assert len(mail.outbox) == 1


def test_registration_duplicate_email(api, user):
    response = register(api, email=user.email, phone_number="9811111111")
    assert response.status_code == 400
    assert "email" in response.data["errors"]


def test_registration_duplicate_phone(api, user):
    response = register(api, email="fresh@example.com", phone_number=user.phone_number)
    assert response.status_code == 400
    assert "phone_number" in response.data["errors"]


def test_registration_invalid_email(api):
    assert register(api, email="not-an-email").status_code == 400


def test_registration_weak_password(api):
    response = register(api, password="weak", confirm_password="weak")
    assert response.status_code == 400
    assert "password" in response.data["errors"]


def test_registration_password_mismatch(api):
    response = register(api, confirm_password="Different@123")
    assert response.status_code == 400


def test_otp_verification_activates_user_and_returns_tokens(api):
    register(api)
    user = User.objects.get(email=PAYLOAD["email"])
    set_known_otp(user)
    response = api.post(VERIFY_URL, {"email": user.email, "otp": "123456",
                                     "purpose": OTPPurpose.REGISTRATION}, format="json")
    assert response.status_code == 200
    assert "access" in response.data["data"]
    user.refresh_from_db()
    assert user.is_verified is True


def test_invalid_otp_rejected(api):
    register(api)
    user = User.objects.get(email=PAYLOAD["email"])
    set_known_otp(user)
    response = api.post(VERIFY_URL, {"email": user.email, "otp": "000000"}, format="json")
    assert response.status_code == 400
    user.refresh_from_db()
    assert user.is_verified is False


def test_otp_is_single_use(api):
    register(api)
    user = User.objects.get(email=PAYLOAD["email"])
    set_known_otp(user)
    api.post(VERIFY_URL, {"email": user.email, "otp": "123456"}, format="json")
    second = api.post(VERIFY_URL, {"email": user.email, "otp": "123456"}, format="json")
    assert second.status_code == 400


def test_expired_otp_rejected(api):
    register(api)
    user = User.objects.get(email=PAYLOAD["email"])
    otp = set_known_otp(user)
    otp.expires_at = timezone.now() - dt.timedelta(minutes=1)
    otp.save()
    response = api.post(VERIFY_URL, {"email": user.email, "otp": "123456"}, format="json")
    assert response.status_code == 400
    assert "expired" in str(response.data["errors"]).lower()


def test_resend_otp_invalidates_old_otp(api, settings):
    settings.OTP_RESEND_COOLDOWN_SECONDS = 0
    register(api)
    user = User.objects.get(email=PAYLOAD["email"])
    old = set_known_otp(user)
    response = api.post(RESEND_URL, {"email": user.email,
                                     "purpose": OTPPurpose.REGISTRATION}, format="json")
    assert response.status_code == 200
    old.refresh_from_db()
    assert old.is_used is True
    assert OTP.objects.active().filter(user=user).count() == 1


def test_resend_otp_rate_limited(api, settings):
    settings.OTP_RESEND_COOLDOWN_SECONDS = 600
    register(api)
    response = api.post(RESEND_URL, {"email": PAYLOAD["email"]}, format="json")
    assert response.status_code == 429


def test_login_success(api, user):
    response = api.post(LOGIN_URL, {"email": user.email, "password": "User@1234"},
                        format="json")
    assert response.status_code == 200
    data = response.data["data"]
    assert data["user"]["role"] == "USER"
    assert data["access"] and data["refresh"]


def test_login_invalid_password(api, user):
    response = api.post(LOGIN_URL, {"email": user.email, "password": "Wrong@1234"},
                        format="json")
    assert response.status_code == 400
    assert response.data["success"] is False


def test_unverified_user_cannot_login(api, db):
    User.objects.create_user(email="pending@example.com", password="Pending@123",
                             full_name="Pending User", phone_number="9800000044")
    response = api.post(LOGIN_URL, {"email": "pending@example.com",
                                    "password": "Pending@123"}, format="json")
    assert response.status_code == 400
    assert "not verified" in response.data["message"].lower()


def test_refresh_rotates_tokens(api, user):
    login = api.post(LOGIN_URL, {"email": user.email, "password": "User@1234"}, format="json")
    refresh = login.data["data"]["refresh"]
    response = api.post(REFRESH_URL, {"refresh": refresh}, format="json")
    assert response.status_code == 200
    assert response.data["data"]["refresh"] != refresh
    assert response.data["data"]["access"]
    # old refresh token is blacklisted
    reused = api.post(REFRESH_URL, {"refresh": refresh}, format="json")
    assert reused.status_code == 400


def test_logout_blacklists_refresh_token(api, user, user_client):
    login = api.post(LOGIN_URL, {"email": user.email, "password": "User@1234"}, format="json")
    refresh = login.data["data"]["refresh"]
    response = user_client.post(LOGOUT_URL, {"refresh": refresh}, format="json")
    assert response.status_code == 200
    assert api.post(REFRESH_URL, {"refresh": refresh}, format="json").status_code == 400


def test_change_password(user_client, user):
    response = user_client.post(CHANGE_PW_URL, {
        "old_password": "User@1234", "new_password": "NewPass@123",
        "confirm_password": "NewPass@123",
    }, format="json")
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password("NewPass@123")


def test_change_password_same_as_old_rejected(user_client):
    response = user_client.post(CHANGE_PW_URL, {
        "old_password": "User@1234", "new_password": "User@1234",
        "confirm_password": "User@1234",
    }, format="json")
    assert response.status_code == 400


def test_change_password_wrong_old_password(user_client):
    response = user_client.post(CHANGE_PW_URL, {
        "old_password": "Nope@1234", "new_password": "NewPass@123",
        "confirm_password": "NewPass@123",
    }, format="json")
    assert response.status_code == 400


def test_forgot_password_rejects_unknown_email(api):
    response = api.post(FORGOT_URL, {"email": "unknown@example.com"}, format="json")
    assert response.status_code == 400
    assert response.data["errors"]["email"] == ["No active account exists with that email."]
    assert len(mail.outbox) == 0


def test_forgot_and_reset_password_flow(api, user):
    assert api.post(FORGOT_URL, {"email": user.email}, format="json").status_code == 200
    set_known_otp(user, OTPPurpose.FORGOT_PASSWORD)
    verify = api.post(VERIFY_FORGOT_URL, {"email": user.email, "otp": "123456"}, format="json")
    assert verify.status_code == 200
    token = verify.data["data"]["reset_token"]
    response = api.post(RESET_URL, {
        "email": user.email, "reset_token": token,
        "new_password": "Reset@1234", "confirm_password": "Reset@1234",
    }, format="json")
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password("Reset@1234")


def test_reset_password_with_invalid_token(api, user):
    response = api.post(RESET_URL, {
        "email": user.email, "reset_token": "tampered",
        "new_password": "Reset@1234", "confirm_password": "Reset@1234",
    }, format="json")
    assert response.status_code == 400


def test_new_otp_invalidates_previous(user):
    first = issue_otp(user=user, purpose=OTPPurpose.FORGOT_PASSWORD, enforce_rate_limit=False)
    issue_otp(user=user, purpose=OTPPurpose.FORGOT_PASSWORD, enforce_rate_limit=False)
    first.refresh_from_db()
    assert first.is_used is True
