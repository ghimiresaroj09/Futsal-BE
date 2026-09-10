"""Test Reserved status in booking responses."""
import datetime as dt

import pytest

from common.enums import BookingStatus, SlotStatus
from common.utils import local_today
from futsal.models import Slot
from bookings.models import Booking

pytestmark = pytest.mark.django_db

BOOKINGS_URL = "/api/v1/bookings/"


def test_pending_booking_shows_reserved_in_slot_status(user_client, futsal, user):
    """When a user views their pending booking, the slot status should show RESERVED."""
    # Create a slot and pending booking
    target_date = local_today() + dt.timedelta(days=2)
    slot = Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(10, 0),
        end_time=dt.time(11, 0),
        status=SlotStatus.BOOKED
    )
    
    booking = Booking.objects.create(
        booking_reference="FSL-TEST-001",
        user=user,
        futsal=futsal,
        slot=slot,
        full_name="Test User",
        email="test@example.com",
        phone_number="9876543210",
        amount=1000,
        status=BookingStatus.PENDING
    )
    
    # Get the booking details
    response = user_client.get(f"{BOOKINGS_URL}{booking.id}/")
    assert response.status_code == 200
    
    # Check that slot status is RESERVED
    assert response.data["data"]["slot"]["status"] == "RESERVED"
    assert response.data["data"]["status"] == BookingStatus.PENDING


def test_confirmed_booking_shows_booked_in_slot_status(user_client, futsal, user):
    """When a user views their confirmed booking, the slot status should show BOOKED."""
    # Create a slot and confirmed booking
    target_date = local_today() + dt.timedelta(days=2)
    slot = Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(11, 0),
        end_time=dt.time(12, 0),
        status=SlotStatus.BOOKED
    )
    
    booking = Booking.objects.create(
        booking_reference="FSL-TEST-002",
        user=user,
        futsal=futsal,
        slot=slot,
        full_name="Test User",
        email="test@example.com",
        phone_number="9876543210",
        amount=1000,
        status=BookingStatus.CONFIRMED
    )
    
    # Get the booking details
    response = user_client.get(f"{BOOKINGS_URL}{booking.id}/")
    assert response.status_code == 200
    
    # Check that slot status is BOOKED (not RESERVED)
    assert response.data["data"]["slot"]["status"] == SlotStatus.BOOKED
    assert response.data["data"]["status"] == BookingStatus.CONFIRMED


def test_booking_list_shows_reserved_for_pending(user_client, futsal, user):
    """When listing bookings, pending bookings should show RESERVED in slot status."""
    # Create multiple bookings with different statuses
    target_date = local_today() + dt.timedelta(days=2)
    
    # Pending booking
    slot1 = Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(10, 0),
        end_time=dt.time(11, 0),
        status=SlotStatus.BOOKED
    )
    booking1 = Booking.objects.create(
        booking_reference="FSL-TEST-003",
        user=user,
        futsal=futsal,
        slot=slot1,
        full_name="Test User",
        email="test@example.com",
        phone_number="9876543210",
        amount=1000,
        status=BookingStatus.PENDING
    )
    
    # Confirmed booking
    slot2 = Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(11, 0),
        end_time=dt.time(12, 0),
        status=SlotStatus.BOOKED
    )
    booking2 = Booking.objects.create(
        booking_reference="FSL-TEST-004",
        user=user,
        futsal=futsal,
        slot=slot2,
        full_name="Test User",
        email="test@example.com",
        phone_number="9876543210",
        amount=1000,
        status=BookingStatus.CONFIRMED
    )
    
    # Get booking list
    response = user_client.get(BOOKINGS_URL)
    assert response.status_code == 200
    
    results = response.data["data"]["results"]
    assert len(results) >= 2
    
    # Find our bookings in the results
    pending_booking = next((b for b in results if b["id"] == str(booking1.id)), None)
    confirmed_booking = next((b for b in results if b["id"] == str(booking2.id)), None)
    
    assert pending_booking is not None
    assert confirmed_booking is not None
    
    # Check statuses
    assert pending_booking["slot"]["status"] == "RESERVED"
    assert confirmed_booking["slot"]["status"] == SlotStatus.BOOKED


def test_admin_booking_list_shows_reserved_for_pending(admin_client, futsal, user):
    """Admin viewing user bookings should also see RESERVED for pending bookings."""
    # Create a pending booking
    target_date = local_today() + dt.timedelta(days=2)
    slot = Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(12, 0),
        end_time=dt.time(13, 0),
        status=SlotStatus.BOOKED
    )
    
    booking = Booking.objects.create(
        booking_reference="FSL-TEST-005",
        user=user,
        futsal=futsal,
        slot=slot,
        full_name="Test User",
        email="test@example.com",
        phone_number="9876543210",
        amount=1000,
        status=BookingStatus.PENDING
    )
    
    # Admin views the booking
    response = admin_client.get(f"/api/v1/admin/bookings/{booking.id}/")
    assert response.status_code == 200
    
    # Admin should also see RESERVED for pending bookings
    assert response.data["data"]["slot"]["status"] == "RESERVED"
    assert response.data["data"]["status"] == BookingStatus.PENDING


def test_cancelled_booking_shows_actual_slot_status(user_client, futsal, user):
    """Cancelled bookings should show the actual slot status (AVAILABLE)."""
    # Create a cancelled booking
    target_date = local_today() + dt.timedelta(days=2)
    slot = Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(13, 0),
        end_time=dt.time(14, 0),
        status=SlotStatus.AVAILABLE  # Slot becomes available after cancellation
    )
    
    booking = Booking.objects.create(
        booking_reference="FSL-TEST-006",
        user=user,
        futsal=futsal,
        slot=slot,
        full_name="Test User",
        email="test@example.com",
        phone_number="9876543210",
        amount=1000,
        status=BookingStatus.CANCELLED
    )
    
    # Get the booking details
    response = user_client.get(f"{BOOKINGS_URL}{booking.id}/")
    assert response.status_code == 200
    
    # Check that slot status shows AVAILABLE (not RESERVED)
    assert response.data["data"]["slot"]["status"] == SlotStatus.AVAILABLE
    assert response.data["data"]["status"] == BookingStatus.CANCELLED


def test_completed_booking_shows_booked_slot_status(user_client, futsal, user):
    """Completed bookings should show BOOKED slot status."""
    # Create a completed booking
    target_date = local_today() + dt.timedelta(days=2)
    slot = Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(14, 0),
        end_time=dt.time(15, 0),
        status=SlotStatus.BOOKED
    )
    
    booking = Booking.objects.create(
        booking_reference="FSL-TEST-007",
        user=user,
        futsal=futsal,
        slot=slot,
        full_name="Test User",
        email="test@example.com",
        phone_number="9876543210",
        amount=1000,
        status=BookingStatus.COMPLETED
    )
    
    # Get the booking details
    response = user_client.get(f"{BOOKINGS_URL}{booking.id}/")
    assert response.status_code == 200
    
    # Check that slot status shows BOOKED (not RESERVED)
    assert response.data["data"]["slot"]["status"] == SlotStatus.BOOKED
    assert response.data["data"]["status"] == BookingStatus.COMPLETED
