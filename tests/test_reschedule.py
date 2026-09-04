"""Booking rescheduling tests."""
import datetime as dt

import pytest

from bookings.services import cancel_booking, create_booking, reschedule_booking
from common.enums import BookingStatus, SlotStatus
from common.exceptions import ConflictError, ServiceError
from futsal.models import Slot

pytestmark = pytest.mark.django_db

URL = "/api/v1/bookings/{}/reschedule/"


def test_successful_reschedule(user_client, booking, second_slot):
    old_slot = booking.slot
    response = user_client.patch(URL.format(booking.id),
                                 {"new_slot_id": str(second_slot.id)}, format="json")
    assert response.status_code == 200
    booking.refresh_from_db()
    old_slot.refresh_from_db()
    second_slot.refresh_from_db()
    assert booking.slot_id == second_slot.id
    assert booking.status == BookingStatus.RESCHEDULED
    assert old_slot.status == SlotStatus.AVAILABLE  # old slot released
    assert second_slot.status == SlotStatus.BOOKED  # new slot booked


def test_reschedule_to_unavailable_slot_fails(user_client, booking, second_slot, other_user):
    create_booking(slot_id=second_slot.id, full_name="Other User",
                   email="other@example.com", phone_number="9800000012", user=other_user)
    response = user_client.patch(URL.format(booking.id),
                                 {"new_slot_id": str(second_slot.id)}, format="json")
    assert response.status_code == 409
    booking.refresh_from_db()
    assert booking.slot_id != second_slot.id  # rolled back


def test_reschedule_to_past_slot_fails(user_client, booking, past_slot):
    response = user_client.patch(URL.format(booking.id),
                                 {"new_slot_id": str(past_slot.id)}, format="json")
    assert response.status_code == 400
    booking.refresh_from_db()
    assert booking.slot_id != past_slot.id


def test_reschedule_other_users_booking_forbidden(api, other_user, booking, second_slot):
    from accounts.services import issue_tokens

    api.credentials(HTTP_AUTHORIZATION=f"Bearer {issue_tokens(other_user)['access']}")
    response = api.patch(URL.format(booking.id), {"new_slot_id": str(second_slot.id)},
                         format="json")
    assert response.status_code == 404


def test_cancelled_booking_cannot_be_rescheduled(booking, second_slot):
    cancel_booking(booking=booking)
    booking.refresh_from_db()
    with pytest.raises(ServiceError):
        reschedule_booking(booking=booking, new_slot_id=second_slot.id)


def test_atomic_rollback_leaves_both_slots_consistent(booking, second_slot, other_user):
    old_slot_id = booking.slot_id
    create_booking(slot_id=second_slot.id, full_name="Other User",
                   email="other@example.com", phone_number="9800000012", user=other_user)
    with pytest.raises(ConflictError):
        reschedule_booking(booking=booking, new_slot_id=second_slot.id)
    booking.refresh_from_db()
    old_slot = Slot.objects.get(pk=old_slot_id)
    assert booking.slot_id == old_slot_id
    assert old_slot.status == SlotStatus.BOOKED


def test_reschedule_to_same_slot_rejected(booking):
    with pytest.raises(ServiceError):
        reschedule_booking(booking=booking, new_slot_id=booking.slot_id)


def test_reschedule_to_missing_slot(user_client, booking):
    response = user_client.patch(URL.format(booking.id),
                                 {"new_slot_id": "11111111-1111-1111-1111-111111111111"},
                                 format="json")
    assert response.status_code in (400, 404)
