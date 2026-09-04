"""Operational dashboard API tests."""
import datetime as dt
from decimal import Decimal

import pytest

from bookings.services import create_booking
from common.enums import PaymentStatus, SlotStatus
from common.utils import local_now, local_today
from futsal.models import Slot

pytestmark = pytest.mark.django_db

DASHBOARD = "/api/v1/dashboard/"


@pytest.fixture
def today_booking(futsal, user):
    now = local_now()
    hour = now.hour + 2
    if hour >= 23:
        pytest.skip("Too late in the day for a same-day slot")
    slot = Slot.objects.create(
        futsal=futsal, date=local_today(), start_time=dt.time(hour), end_time=dt.time(hour + 1)
    )
    return create_booking(
        slot_id=slot.id, full_name="Today User", email="today@example.com",
        phone_number="9800000077", user=user, payment_status=PaymentStatus.PAID,
    )


def test_dashboard_returns_documented_operational_sections(admin_client, today_booking):
    response = admin_client.get(DASHBOARD)

    assert response.status_code == 200
    data = response.data["data"]
    assert {"date", "timezone", "facility", "operational_stats", "slot_availability", "todays_schedule", "facility_snapshot", "generated_at"} <= set(data)
    assert data["operational_stats"]["todays_bookings"] == 1
    assert Decimal(str(data["operational_stats"]["todays_revenue"])) == today_booking.amount
    assert data["slot_availability"][0]["status"] == SlotStatus.BOOKED
    assert str(data["todays_schedule"][0]["booking_id"]) == str(today_booking.id)


def test_dashboard_supports_operating_date_and_rejects_invalid_date(admin_client, booking):
    response = admin_client.get(f"{DASHBOARD}?date={booking.slot.date}")
    assert response.status_code == 200
    assert str(response.data["data"]["date"]) == booking.slot.date.isoformat()
    assert admin_client.get(f"{DASHBOARD}?date=invalid").status_code == 400


def test_dashboard_requires_admin(user_client):
    assert user_client.get(DASHBOARD).status_code == 403
