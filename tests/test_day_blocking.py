"""Whole-day blocking (holidays, maintenance)."""
import datetime as dt

import pytest

from bookings.models import Booking
from common.enums import BookingStatus, PaymentStatus, SlotStatus
from common.utils import local_today
from futsal.models import FutsalClosure, Slot
from futsal.services import block_day, generate_slots_for_date, unblock_day

pytestmark = pytest.mark.django_db

BLOCK = "/api/v1/admin/slots/block-day/"
BLOCK_RANGE = "/api/v1/admin/slots/block-range/"
UNBLOCK = "/api/v1/admin/slots/unblock-day/"
CLOSURES = "/api/v1/admin/slots/closures/"


@pytest.fixture
def day(futsal):
    """A future date fully populated with hourly slots."""
    date = local_today() + dt.timedelta(days=3)
    generate_slots_for_date(date=date)
    return date


def test_block_day_blocks_every_available_slot(admin_client, day):
    response = admin_client.post(BLOCK, {"date": day.isoformat(),
                                         "reason": "Dashain holiday"}, format="json")
    assert response.status_code == 200
    assert response.data["data"]["blocked_slots"] == 16
    assert Slot.objects.filter(date=day, status=SlotStatus.BLOCKED).count() == 16
    assert Slot.objects.filter(date=day, status=SlotStatus.AVAILABLE).count() == 0


def test_block_day_records_closure_with_reason(admin_client, day):
    admin_client.post(BLOCK, {"date": day.isoformat(), "reason": "Maintenance"},
                      format="json")
    closure = FutsalClosure.objects.get(date=day)
    assert closure.reason == "Maintenance"
    assert closure.created_by is not None


def test_blocked_day_rejects_booking_with_409(user_client, admin_client, day):
    admin_client.post(BLOCK, {"date": day.isoformat(), "reason": "Holiday"}, format="json")
    slot = Slot.objects.filter(date=day).first()
    response = user_client.post("/api/v1/bookings/", {
        "slot_id": str(slot.id), "full_name": "John Doe",
        "email": "john@example.com", "phone_number": "9800000000",
    }, format="json")
    assert response.status_code == 409
    assert "closed" in response.data["message"].lower()
    assert "Holiday" in response.data["message"]


def test_generation_skips_closed_day(admin_client, futsal):
    date = local_today() + dt.timedelta(days=4)
    block_day(date=date, reason="Closed")
    assert generate_slots_for_date(date=date) == []
    assert Slot.objects.filter(date=date).count() == 0


def test_block_day_preserves_existing_bookings_by_default(admin_client, futsal, user, day):
    from bookings.services import create_booking

    slot = Slot.objects.filter(date=day).first()
    booking = create_booking(slot_id=slot.id, full_name="John Doe",
                             email="john@example.com", phone_number="9800000000",
                             user=user, payment_status=PaymentStatus.PAID)
    response = admin_client.post(BLOCK, {"date": day.isoformat()}, format="json")
    data = response.data["data"]
    assert data["skipped_booked_slots"] == 1
    assert data["cancelled_bookings"] == 0
    assert data["blocked_slots"] == 15
    booking.refresh_from_db()
    slot.refresh_from_db()
    assert booking.status == BookingStatus.CONFIRMED
    assert slot.status == SlotStatus.BOOKED


def test_block_day_can_cancel_and_refund_bookings(admin_client, futsal, user, day):
    from bookings.services import create_booking

    slot = Slot.objects.filter(date=day).first()
    booking = create_booking(slot_id=slot.id, full_name="John Doe",
                             email="john@example.com", phone_number="9800000000",
                             user=user, payment_status=PaymentStatus.PAID)
    response = admin_client.post(BLOCK, {"date": day.isoformat(), "reason": "Flooded",
                                         "cancel_bookings": True}, format="json")
    data = response.data["data"]
    assert data["cancelled_bookings"] == 1
    assert data["blocked_slots"] == 16
    booking.refresh_from_db()
    assert booking.status == BookingStatus.CANCELLED
    assert booking.payment.payment_status == PaymentStatus.REFUNDED
    assert Slot.objects.filter(date=day, status=SlotStatus.AVAILABLE).count() == 0


def test_unblock_day_restores_availability(admin_client, day):
    admin_client.post(BLOCK, {"date": day.isoformat()}, format="json")
    response = admin_client.post(UNBLOCK, {"date": day.isoformat()}, format="json")
    assert response.status_code == 200
    assert response.data["data"]["released_slots"] == 16
    assert Slot.objects.filter(date=day, status=SlotStatus.AVAILABLE).count() == 16
    assert not FutsalClosure.objects.filter(date=day).exists()


def test_booking_works_again_after_unblock(user_client, admin_client, day):
    admin_client.post(BLOCK, {"date": day.isoformat()}, format="json")
    admin_client.post(UNBLOCK, {"date": day.isoformat()}, format="json")
    slot = Slot.objects.filter(date=day).first()
    response = user_client.post("/api/v1/bookings/", {
        "slot_id": str(slot.id), "full_name": "John Doe",
        "email": "john@example.com", "phone_number": "9800000000",
    }, format="json")
    assert response.status_code == 201


def test_block_range(admin_client, futsal):
    start = local_today() + dt.timedelta(days=10)
    for offset in range(3):
        generate_slots_for_date(date=start + dt.timedelta(days=offset))
    response = admin_client.post(BLOCK_RANGE, {
        "start_date": start.isoformat(),
        "end_date": (start + dt.timedelta(days=2)).isoformat(),
        "reason": "Tournament",
    }, format="json")
    assert response.status_code == 200
    assert response.data["data"]["days_blocked"] == 3
    assert response.data["data"]["blocked_slots"] == 48
    assert FutsalClosure.objects.count() == 3


def test_block_day_is_idempotent(admin_client, day):
    admin_client.post(BLOCK, {"date": day.isoformat()}, format="json")
    second = admin_client.post(BLOCK, {"date": day.isoformat(), "reason": "Updated"},
                               format="json")
    assert second.status_code == 200
    assert second.data["data"]["blocked_slots"] == 0
    assert FutsalClosure.objects.filter(date=day).count() == 1
    assert FutsalClosure.objects.get(date=day).reason == "Updated"


def test_cannot_block_past_date(admin_client):
    response = admin_client.post(
        BLOCK, {"date": (local_today() - dt.timedelta(days=1)).isoformat()}, format="json")
    assert response.status_code == 400


def test_block_range_rejects_reversed_range(admin_client):
    start = local_today() + dt.timedelta(days=5)
    response = admin_client.post(BLOCK_RANGE, {
        "start_date": start.isoformat(),
        "end_date": (start - dt.timedelta(days=2)).isoformat(),
    }, format="json")
    assert response.status_code == 400


def test_closures_listing(admin_client, day):
    admin_client.post(BLOCK, {"date": day.isoformat(), "reason": "Holiday"}, format="json")
    response = admin_client.get(CLOSURES)
    assert response.status_code == 200
    assert response.data["data"]["count"] == 1
    assert response.data["data"]["results"][0]["reason"] == "Holiday"


@pytest.mark.parametrize("url", [BLOCK, BLOCK_RANGE, UNBLOCK])
def test_day_blocking_requires_admin(user_client, url):
    assert user_client.post(url, {}, format="json").status_code == 403


def test_users_see_no_available_slots_on_blocked_day(api, admin_client, day):
    admin_client.post(BLOCK, {"date": day.isoformat()}, format="json")
    response = api.get(f"/api/v1/slots/?date={day.isoformat()}&status=AVAILABLE")
    assert response.data["data"]["count"] == 0
