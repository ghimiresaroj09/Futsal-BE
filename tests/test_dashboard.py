"""Dashboard API tests."""
import datetime as dt
from decimal import Decimal

import pytest

from bookings.services import create_booking
from common.enums import PaymentStatus, SlotStatus
from common.utils import local_now, local_today
from dashboard.selectors import slot_analytics
from futsal.models import Slot

pytestmark = pytest.mark.django_db

DASHBOARD = "/api/v1/admin/dashboard/"


@pytest.fixture
def today_booking(futsal, user):
    """A booking for later today (or tomorrow if the day is nearly over)."""
    now = local_now()
    hour = now.hour + 2
    if hour >= 23:
        pytest.skip("Too late in the day for a same-day slot")
    slot = Slot.objects.create(futsal=futsal, date=local_today(),
                               start_time=dt.time(hour, 0), end_time=dt.time(hour + 1, 0))
    return create_booking(slot_id=slot.id, full_name="Today User", email="today@example.com",
                          phone_number="9800000077", user=user,
                          payment_status=PaymentStatus.PAID)


def test_dashboard_today_overview(admin_client, today_booking):
    data = admin_client.get(DASHBOARD).data["data"]["today"]
    assert data["bookings"] == 1
    assert Decimal(str(data["revenue"])) == today_booking.amount
    assert data["booked_slots"] == 1
    assert data["available_slots"] == 0


def test_dashboard_requires_admin(user_client):
    assert user_client.get(DASHBOARD).status_code == 403


def test_slot_analytics_and_occupancy(admin_client, futsal, booking):
    Slot.objects.create(futsal=futsal, date=booking.slot.date, start_time=dt.time(16, 0),
                        end_time=dt.time(17, 0))
    Slot.objects.create(futsal=futsal, date=booking.slot.date, start_time=dt.time(17, 0),
                        end_time=dt.time(18, 0), status=SlotStatus.BLOCKED)
    data = admin_client.get("/api/v1/admin/dashboard/slots/").data["data"]
    assert data["booked"] == 1
    assert data["available"] == 1
    assert data["blocked"] == 1
    assert data["occupancy_rate"] == 50.0


def test_occupancy_handles_division_by_zero(db):
    assert slot_analytics()["occupancy_rate"] == 0.0


@pytest.mark.parametrize("period", ["day", "week", "month"])
def test_revenue_graph_data(admin_client, booking, period):
    response = admin_client.get(f"{DASHBOARD}revenue/?period={period}")
    assert response.status_code == 200
    series = response.data["data"]
    assert isinstance(series, list) and series
    assert {"date", "revenue"} <= set(series[0])


@pytest.mark.parametrize("period", ["day", "week", "month"])
def test_bookings_graph_data(admin_client, booking, period):
    response = admin_client.get(f"{DASHBOARD}bookings/?period={period}")
    series = response.data["data"]
    assert response.status_code == 200
    assert series[0]["bookings"] == 1


def test_invalid_period_defaults_to_day(admin_client, booking):
    assert admin_client.get(f"{DASHBOARD}revenue/?period=nonsense").status_code == 200
