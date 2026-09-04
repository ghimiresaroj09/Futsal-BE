"""Query helpers for accounts."""
from __future__ import annotations

from accounts.models import User


def get_user_by_email(email: str) -> User | None:
    return User.objects.filter(email=(email or "").lower().strip()).first()
