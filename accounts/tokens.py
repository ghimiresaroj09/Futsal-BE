"""Short-lived signed password-reset tokens issued after OTP verification."""
from __future__ import annotations

from django.core import signing

RESET_SALT = "futsal.password.reset"
RESET_TOKEN_MAX_AGE = 15 * 60  # seconds


def make_reset_token(user_id) -> str:
    return signing.dumps({"user_id": str(user_id)}, salt=RESET_SALT)


def read_reset_token(token: str) -> str | None:
    try:
        data = signing.loads(token, salt=RESET_SALT, max_age=RESET_TOKEN_MAX_AGE)
    except signing.BadSignature:
        return None
    return data.get("user_id")
