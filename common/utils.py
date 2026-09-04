"""Small shared helpers."""
from __future__ import annotations

import datetime as dt
import secrets

from django.utils import timezone


def generate_numeric_code(length: int = 6) -> str:
    """Cryptographically secure numeric code."""
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def local_now() -> dt.datetime:
    return timezone.localtime(timezone.now())


def local_today() -> dt.date:
    return local_now().date()


def combine_local(date: dt.date, time: dt.time) -> dt.datetime:
    """Combine a date and time into an aware datetime in the active timezone."""
    naive = dt.datetime.combine(date, time)
    return timezone.make_aware(naive, timezone.get_current_timezone())


def parse_date(value: str | None) -> dt.date | None:
    if not value:
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None
