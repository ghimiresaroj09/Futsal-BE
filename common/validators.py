"""Reusable validators."""
from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

PHONE_REGEX = re.compile(r"^\+?[0-9]{7,15}$")
FULL_NAME_REGEX = re.compile(r"^[A-Za-z][A-Za-z .'-]{1,99}$")


class StrongPasswordValidator:
    """Requires upper, lower, digit and special character."""

    def __init__(self, min_length: int = 8) -> None:
        self.min_length = min_length

    def validate(self, password: str, user=None) -> None:
        errors = []
        if len(password) < self.min_length:
            errors.append(_("Password must be at least %d characters long.") % self.min_length)
        if not re.search(r"[A-Z]", password):
            errors.append(_("Password must contain an uppercase letter."))
        if not re.search(r"[a-z]", password):
            errors.append(_("Password must contain a lowercase letter."))
        if not re.search(r"[0-9]", password):
            errors.append(_("Password must contain a number."))
        if not re.search(r"[^A-Za-z0-9]", password):
            errors.append(_("Password must contain a special character."))
        if errors:
            raise ValidationError(errors, code="password_too_weak")

    def get_help_text(self) -> str:
        return _(
            "Your password must contain uppercase, lowercase, a number and a special character."
        )


def validate_phone_number(value: str) -> str:
    if not PHONE_REGEX.match(value or ""):
        raise ValidationError(
            _("Enter a valid phone number (7-15 digits, optional leading +)."),
            code="invalid_phone",
        )
    return value


def validate_full_name(value: str) -> str:
    value = (value or "").strip()
    if not FULL_NAME_REGEX.match(value):
        raise ValidationError(
            _("Enter a valid full name (letters, spaces, apostrophes and hyphens only)."),
            code="invalid_full_name",
        )
    return value


IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
VIDEO_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "webm"}


def _extension(name: str) -> str:
    return name.rsplit(".", 1)[-1].lower() if "." in (name or "") else ""


def _validate_upload(value, *, allowed: set[str], max_mb: int, label: str):
    extension = _extension(getattr(value, "name", ""))
    if extension not in allowed:
        raise ValidationError(
            _("Unsupported %(label)s format '.%(ext)s'. Allowed: %(allowed)s.")
            % {"label": label, "ext": extension, "allowed": ", ".join(sorted(allowed))},
            code="invalid_extension",
        )
    if (getattr(value, "size", 0) or 0) > max_mb * 1024 * 1024:
        raise ValidationError(
            _("%(label)s must be %(max)d MB or smaller.")
            % {"label": label.capitalize(), "max": max_mb},
            code="file_too_large",
        )
    return value


def validate_image_upload(value):
    from django.conf import settings

    return _validate_upload(value, allowed=IMAGE_EXTENSIONS,
                            max_mb=getattr(settings, "MAX_IMAGE_UPLOAD_MB", 5), label="image")


def validate_video_upload(value):
    from django.conf import settings

    return _validate_upload(value, allowed=VIDEO_EXTENSIONS,
                            max_mb=getattr(settings, "MAX_VIDEO_UPLOAD_MB", 100), label="video")
