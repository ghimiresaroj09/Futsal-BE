"""Test Reserved status for pending bookings in slot listing."""
import datetime as dt

import pytest

from common.enums import BookingStatus, SlotStatus
from common.utils import local_today
from futsal.models import Slot
from bookings.models import Booking

pytestmark = pytest.mark.django_db

PUBLIC_SLOTS = "/api/v1/slots/"


def test_pending_booking_shows_reserved_for_users(api, user_client, futsal, user):
    """Non-admin users should see RESERVED status for slots with pending bookings."""
    # Create a slot
    target_date = local_today() + dt.timedelta(days=2)
    slot = Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(10, 0),
        end_time=dt.time(11, 0),
        status=SlotStatus.BOOKED
    )
    
    # Create a pending booking for the slot
    booking = Booking.objects.create(
        booking_reference="TEST123",
        user=user,
        futsal=futsal,
        slot=slot,
        full_name="Test User",
        email="test@example.com",
        phone_number="1234567890",
        amount=1000,
        status=BookingStatus.PENDING
    )
    
    # User should see RESERVED
    response = user_client.get(f"{PUBLIC_SLOTS}?date={target_date.isoformat()}")
    assert response.status_code == 200
    results = response.data["data"]["results"]
    assert len(results) == 1
    assert results[0]["status"] == "RESERVED"


def test_pending_booking_shows_reserved_for_admin(admin_client, futsal, user):
    """Admin users should also see RESERVED status for pending bookings."""
    # Create a slot
    target_date = local_today() + dt.timedelta(days=2)
    slot = Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(10, 0),
        end_time=dt.time(11, 0),
        status=SlotStatus.BOOKED
    )
    
    # Create a pending booking for the slot
    booking = Booking.objects.create(
        booking_reference="TEST456",
        user=user,
        futsal=futsal,
        slot=slot,
        full_name="Test User",
        email="test@example.com",
        phone_number="1234567890",
        amount=1000,
        status=BookingStatus.PENDING
    )
    
    # Admin should also see RESERVED (same as public users)
    response = admin_client.get(f"{PUBLIC_SLOTS}?date={target_date.isoformat()}")
    assert response.status_code == 200
    results = response.data["data"]["results"]
    assert len(results) == 1
    assert results[0]["status"] == "RESERVED"


def test_confirmed_booking_shows_booked_for_users(user_client, futsal, user):
    """Non-admin users should see BOOKED status for slots with confirmed bookings."""
    # Create a slot
    target_date = local_today() + dt.timedelta(days=2)
    slot = Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(11, 0),
        end_time=dt.time(12, 0),
        status=SlotStatus.BOOKED
    )
    
    # Create a confirmed booking for the slot
    booking = Booking.objects.create(
        booking_reference="TEST789",
        user=user,
        futsal=futsal,
        slot=slot,
        full_name="Test User",
        email="test@example.com",
        phone_number="1234567890",
        amount=1000,
        status=BookingStatus.CONFIRMED
    )
    
    # User should see BOOKED (not RESERVED)
    response = user_client.get(f"{PUBLIC_SLOTS}?date={target_date.isoformat()}")
    assert response.status_code == 200
    results = response.data["data"]["results"]
    assert len(results) == 1
    assert results[0]["status"] == SlotStatus.BOOKED


def test_available_slot_shows_available_for_users(user_client, futsal):
    """Non-admin users should see AVAILABLE status for slots without bookings."""
    # Create an available slot
    target_date = local_today() + dt.timedelta(days=2)
    slot = Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(12, 0),
        end_time=dt.time(13, 0),
        status=SlotStatus.AVAILABLE
    )
    
    # User should see AVAILABLE
    response = user_client.get(f"{PUBLIC_SLOTS}?date={target_date.isoformat()}")
    assert response.status_code == 200
    results = response.data["data"]["results"]
    assert len(results) == 1
    assert results[0]["status"] == SlotStatus.AVAILABLE


def test_date_wise_endpoint_shows_reserved_for_pending(user_client, futsal, user):
    """Date-wise endpoint should also show RESERVED for pending bookings."""
    # Create a slot with pending booking
    target_date = local_today() + dt.timedelta(days=2)
    slot = Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(13, 0),
        end_time=dt.time(14, 0),
        status=SlotStatus.BOOKED
    )
    
    booking = Booking.objects.create(
        booking_reference="TEST999",
        user=user,
        futsal=futsal,
        slot=slot,
        full_name="Test User",
        email="test@example.com",
        phone_number="1234567890",
        amount=1000,
        status=BookingStatus.PENDING
    )
    
    # User should see RESERVED on date-wise endpoint
    response = user_client.get(f"{PUBLIC_SLOTS}date-wise/?date={target_date.isoformat()}")
    assert response.status_code == 200
    results = response.data["data"]["results"]
    assert len(results) == 1
    assert results[0]["status"] == "RESERVED"


def test_anonymous_user_sees_reserved_for_pending(api, futsal, user):
    """Anonymous (unauthenticated) users should also see RESERVED for pending bookings."""
    # Create a slot with pending booking
    target_date = local_today() + dt.timedelta(days=2)
    slot = Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(14, 0),
        end_time=dt.time(15, 0),
        status=SlotStatus.BOOKED
    )
    
    booking = Booking.objects.create(
        booking_reference="TEST000",
        user=user,
        futsal=futsal,
        slot=slot,
        full_name="Test User",
        email="test@example.com",
        phone_number="1234567890",
        amount=1000,
        status=BookingStatus.PENDING
    )
    
    # Anonymous user should see RESERVED
    response = api.get(f"{PUBLIC_SLOTS}?date={target_date.isoformat()}")
    assert response.status_code == 200
    results = response.data["data"]["results"]
    assert len(results) == 1
    assert results[0]["status"] == "RESERVED"
