"""Serverless cron endpoint that replaces Celery Beat on Render free."""
from __future__ import annotations

import datetime as dt

import pytest

from bookings.services import create_booking
from common.enums import PaymentStatus
from common.utils import local_now
from futsal.models import Slot

pytestmark = pytest.mark.django_db

URL = "/api/v1/internal/cron/reminders/"


@pytest.fixture
def booking_in_one_hour(futsal, user, monkeypatch):
    frozen = local_now().replace(hour=12, minute=0, second=0, microsecond=0)
    monkeypatch.setattr("notifications.services.timezone.now", lambda: frozen)
    start = frozen + dt.timedelta(minutes=58)
    slot = Slot.objects.create(
        futsal=futsal,
        date=start.date(),
        start_time=start.time().replace(second=0, microsecond=0),
        end_time=(start + dt.timedelta(hours=1)).time().replace(second=0, microsecond=0),
    )
    monkeypatch.setattr("bookings.services.local_now", lambda: frozen - dt.timedelta(hours=1))
    monkeypatch.setattr("futsal.models.local_now", lambda: frozen - dt.timedelta(hours=1))
    return create_booking(
        slot_id=slot.id,
        full_name="Cron User",
        email="cron@example.com",
        phone_number="9800000077",
        user=user,
        payment_status=PaymentStatus.PAID,
    )


def test_cron_requires_secret(api, settings):
    settings.CRON_SECRET = "s3cret"
    assert api.get(URL).status_code == 401


def test_cron_rejects_wrong_secret(api, settings):
    settings.CRON_SECRET = "s3cret"
    assert api.get(URL, HTTP_AUTHORIZATION="Bearer nope").status_code == 401


def test_cron_accepts_correct_secret(api, settings):
    settings.CRON_SECRET = "s3cret"
    response = api.get(URL, HTTP_AUTHORIZATION="Bearer s3cret")
    assert response.status_code == 200
    assert response.data["data"] == {"sent": 0, "failed": 0}


def test_cron_fails_closed_when_no_secret_configured(api, settings):
    settings.CRON_SECRET = ""
    assert api.get(URL, HTTP_AUTHORIZATION="Bearer anything").status_code == 401
    assert api.get(URL).status_code == 401


def test_cron_sends_due_reminder_and_dedups(api, settings, booking_in_one_hour):
    from django.core import mail

    settings.CRON_SECRET = "s3cret"
    first = api.get(URL, HTTP_AUTHORIZATION="Bearer s3cret")
    assert first.data["data"]["sent"] == 1
    assert len(mail.outbox) == 1
    second = api.get(URL, HTTP_AUTHORIZATION="Bearer s3cret")
    assert second.data["data"]["sent"] == 0
