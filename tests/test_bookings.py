"""Booking creation, cancellation and completion tests."""
from decimal import Decimal

import pytest
from django.core import mail

from bookings.models import Booking
from bookings.services import cancel_booking, create_booking, mark_completed, reschedule_booking
from common.enums import BookingSource, BookingStatus, PaymentStatus, SlotStatus
from common.exceptions import ConflictError, ServiceError
from notifications.models import AdminNotification

pytestmark = pytest.mark.django_db

BOOKINGS_URL = "/api/v1/bookings/"
ADMIN_BOOKINGS_URL = "/api/v1/admin/bookings/"


def body(slot):
    return {"slot_id": str(slot.id), "full_name": "John Doe",
            "email": "john@example.com", "phone_number": "9800000000"}


def test_user_can_book_available_slot(user_client, slot):
    response = user_client.post(BOOKINGS_URL, body(slot), format="json")
    assert response.status_code == 201
    data = response.data["data"]
    assert data["booking_reference"].startswith("FSL-")
    slot.refresh_from_db()
    assert slot.status == SlotStatus.BOOKED


@pytest.mark.django_db(transaction=True)
def test_customer_booking_is_pending_notifies_admin_and_waits_to_email(
    user_client, admin_client, admin_user, slot
):
    """The customer is emailed only when an admin confirms the request."""
    mail.outbox.clear()

    response = user_client.post(BOOKINGS_URL, body(slot), format="json")

    assert response.status_code == 201
    booking = Booking.objects.get(pk=response.data["data"]["id"])
    assert booking.status == BookingStatus.PENDING
    assert AdminNotification.objects.filter(recipient=admin_user, booking=booking).exists()
    assert len(mail.outbox) == 0

    response = admin_client.patch(
        f"{ADMIN_BOOKINGS_URL}{booking.id}/", {"status": BookingStatus.CONFIRMED}, format="json"
    )

    assert response.status_code == 200
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [booking.email]
    assert "Booking confirmed" in mail.outbox[0].subject


def test_user_can_update_booking_contact_details(user_client, booking):
    response = user_client.patch(
        f"{BOOKINGS_URL}{booking.id}/",
        {
            "email": "updated@example.com",
            "full_name": "Updated User",
            "phone_number": "9843951178",
            "notes": "We are ready.",
        },
        format="json",
    )

    assert response.status_code == 200
    booking.refresh_from_db()
    assert booking.email == "updated@example.com"
    assert booking.full_name == "Updated User"
    assert booking.phone_number == "9843951178"
    assert booking.notes == "We are ready."


def test_user_booking_update_does_not_allow_other_fields(user_client, booking):
    response = user_client.patch(
        f"{BOOKINGS_URL}{booking.id}/",
        {"status": BookingStatus.CANCELLED, "amount": "1.00"},
        format="json",
    )

    assert response.status_code == 200
    booking.refresh_from_db()
    assert booking.status == BookingStatus.CONFIRMED
    assert booking.amount == Decimal("1000.00")


def test_booking_requires_authentication(api, slot):
    assert api.post(BOOKINGS_URL, body(slot), format="json").status_code == 401


def test_booking_stores_contact_snapshot(user_client, slot, user):
    user_client.post(BOOKINGS_URL, body(slot), format="json")
    booking = Booking.objects.get()
    user.full_name = "Renamed"
    user.email = "renamed@example.com"
    user.save()
    booking.refresh_from_db()
    assert booking.full_name == "John Doe"
    assert booking.email == "john@example.com"


def test_booking_amount_is_snapshotted(user_client, slot, futsal):
    user_client.post(BOOKINGS_URL, body(slot), format="json")
    booking = Booking.objects.get()
    futsal.price_per_slot = Decimal("5000.00")
    futsal.save()
    booking.refresh_from_db()
    assert booking.amount == Decimal("1000.00")


def test_already_booked_slot_returns_409(user_client, other_user, slot, booking):
    response = user_client.post(BOOKINGS_URL, body(slot), format="json")
    assert response.status_code == 409
    assert response.data["success"] is False


def test_duplicate_booking_by_same_user_rejected(user_client, slot):
    user_client.post(BOOKINGS_URL, body(slot), format="json")
    assert user_client.post(BOOKINGS_URL, body(slot), format="json").status_code == 409


def test_cannot_book_past_slot(user_client, past_slot):
    response = user_client.post(BOOKINGS_URL, body(past_slot), format="json")
    assert response.status_code == 400


def test_cannot_book_blocked_slot(user_client, slot):
    slot.status = SlotStatus.BLOCKED
    slot.save()
    assert user_client.post(BOOKINGS_URL, body(slot), format="json").status_code == 409


def test_invalid_slot_returns_error(user_client):
    response = user_client.post(BOOKINGS_URL, {
        "full_name": "John Doe", "email": "john@example.com",
        "phone_number": "9800000000",
        "slot_id": "11111111-1111-1111-1111-111111111111",
    }, format="json")
    assert response.status_code in (400, 404)


def test_booking_validation_errors(user_client, slot):
    response = user_client.post(BOOKINGS_URL, {"slot_id": str(slot.id)}, format="json")
    assert response.status_code == 400
    assert "full_name" in response.data["errors"]


def test_user_sees_own_and_admin_created_bookings(
    user_client, admin_user, user, booking, other_user, second_slot, third_slot
):
    create_booking(slot_id=second_slot.id, full_name="Other", email="other@example.com",
                   phone_number="9800000012", user=other_user)
    admin_created_booking = create_booking(
        slot_id=third_slot.id,
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
        created_by=admin_user,
        source=BookingSource.ADMIN,
    )

    response = user_client.get(BOOKINGS_URL)
    results = response.data["data"]
    assert results["count"] == 2
    assert {item["id"] for item in results["results"]} == {
        str(booking.id), str(admin_created_booking.id)
    }


def test_booking_history_filters(user_client, booking):
    date = booking.slot.date.isoformat()
    assert user_client.get(f"{BOOKINGS_URL}?date={date}").data["data"]["count"] == 1
    assert user_client.get(f"{BOOKINGS_URL}?status=CONFIRMED").data["data"]["count"] == 1
    assert user_client.get(f"{BOOKINGS_URL}?status=CANCELLED").data["data"]["count"] == 0


def test_booking_detail(user_client, booking):
    response = user_client.get(f"{BOOKINGS_URL}{booking.id}/")
    assert response.status_code == 200
    assert response.data["data"]["booking_reference"] == booking.booking_reference


def test_cancel_booking_releases_slot(user_client, booking):
    response = user_client.post(f"{BOOKINGS_URL}{booking.id}/cancel/", {"reason": "Rain"},
                                format="json")
    assert response.status_code == 200
    booking.refresh_from_db()
    booking.slot.refresh_from_db()
    assert booking.status == BookingStatus.CANCELLED
    assert booking.slot.status == SlotStatus.AVAILABLE


def test_cancelled_booking_refunds_payment(booking):
    cancel_booking(booking=booking, reason="test")
    booking.refresh_from_db()
    assert booking.payment.payment_status == PaymentStatus.REFUNDED
    assert booking.payment.refunded_amount == booking.amount


def test_slot_can_be_rebooked_after_cancellation(user_client, booking, slot):
    cancel_booking(booking=booking)
    response = user_client.post(BOOKINGS_URL, body(slot), format="json")
    assert response.status_code == 201


def test_double_cancellation_rejected(booking):
    cancel_booking(booking=booking)
    with pytest.raises(Exception):
        cancel_booking(booking=booking)


def test_mark_completed(booking):
    booking = mark_completed(booking=booking)
    assert booking.status == BookingStatus.COMPLETED


def test_invalid_state_transition_rejected(booking):
    from bookings.services import change_booking_status

    mark_completed(booking=booking)
    booking.refresh_from_db()
    with pytest.raises(Exception):
        change_booking_status(booking=booking, new_status=BookingStatus.CONFIRMED)


def test_admin_can_create_booking_on_behalf(admin_client, slot):
    response = admin_client.post(ADMIN_BOOKINGS_URL, body(slot), format="json")
    assert response.status_code == 201
    assert response.data["data"]["booking_source"] == BookingSource.ADMIN
    booking = Booking.objects.get()
    assert booking.created_by is not None


def test_admin_can_record_and_update_an_advance_payment(admin_client, slot):
    response = admin_client.post(
        ADMIN_BOOKINGS_URL,
        {**body(slot), "advance_amount": "250.00", "payment_method": "ESEWA"},
        format="json",
    )

    assert response.status_code == 201
    data = response.data["data"]
    assert data["payment_status"] == PaymentStatus.ADVANCED
    assert Decimal(data["advance_amount"]) == Decimal("250.00")
    assert Decimal(data["remaining_amount"]) == Decimal("750.00")
    assert data["payment_method"] == "ESEWA"

    response = admin_client.patch(
        f"{ADMIN_BOOKINGS_URL}{data['id']}/",
        {"advance_amount": "400.00", "payment_method": "KHALTI"},
        format="json",
    )

    assert response.status_code == 200
    data = response.data["data"]
    assert data["payment_status"] == PaymentStatus.ADVANCED
    assert Decimal(data["advance_amount"]) == Decimal("400.00")
    assert Decimal(data["remaining_amount"]) == Decimal("600.00")
    assert data["payment_method"] == "KHALTI"


@pytest.mark.parametrize("booking_status", [BookingStatus.PENDING, BookingStatus.RESCHEDULED])
def test_admin_can_edit_booking_when_submitting_its_unchanged_status(
    admin_client, user, slot, second_slot, booking_status
):
    booking = create_booking(
        slot_id=slot.id,
        full_name="Original Name",
        email="original@example.com",
        phone_number="9800000001",
        user=user,
        status=BookingStatus.PENDING,
    )
    if booking_status == BookingStatus.RESCHEDULED:
        booking = reschedule_booking(
            booking=booking, new_slot_id=second_slot.id,
        )

    response = admin_client.patch(
        f"{ADMIN_BOOKINGS_URL}{booking.id}/",
        {
            "status": booking_status,
            "full_name": "Saroj Ghimire",
            "email": "ghimires090@gmail.com",
            "phone_number": "9843951178",
            "notes": "We are ready",
            "advance_amount": "500.00",
            "payment_method": "ESEWA",
        },
        format="json",
    )

    assert response.status_code == 200
    booking.refresh_from_db()
    assert booking.status == booking_status
    assert booking.full_name == "Saroj Ghimire"
    assert booking.email == "ghimires090@gmail.com"
    assert booking.phone_number == "9843951178"
    assert booking.notes == "We are ready"
    assert booking.payment.advance_amount == Decimal("500.00")
    assert booking.payment.payment_method == "ESEWA"


def test_completion_marks_advanced_payment_paid_and_cancellation_refunds_advance(
    admin_client, user, slot, second_slot
):
    advanced = create_booking(
        slot_id=slot.id, full_name="Advance User", email="advance@example.com",
        phone_number="9800000091", user=user, advance_amount=Decimal("200.00"),
    )
    response = admin_client.patch(
        f"{ADMIN_BOOKINGS_URL}{advanced.id}/", {"status": BookingStatus.COMPLETED}, format="json"
    )
    assert response.status_code == 200
    advanced.refresh_from_db()
    assert advanced.payment.payment_status == PaymentStatus.PAID

    refundable = create_booking(
        slot_id=second_slot.id, full_name="Refund User", email="refund@example.com",
        phone_number="9800000092", user=user, advance_amount=Decimal("300.00"),
    )
    cancel_booking(booking=refundable)
    refundable.refresh_from_db()
    assert refundable.payment.payment_status == PaymentStatus.REFUNDED
    assert refundable.payment.refunded_amount == Decimal("300.00")


@pytest.mark.django_db(transaction=True)
def test_admin_pending_booking_does_not_email_until_confirmed(admin_client, slot):
    mail.outbox.clear()

    response = admin_client.post(ADMIN_BOOKINGS_URL, body(slot), format="json")

    assert response.status_code == 201
    booking = Booking.objects.get(pk=response.data["data"]["id"])
    assert booking.status == BookingStatus.PENDING
    assert len(mail.outbox) == 0

    response = admin_client.patch(
        f"{ADMIN_BOOKINGS_URL}{booking.id}/", {"status": BookingStatus.CONFIRMED}, format="json"
    )

    assert response.status_code == 200
    assert len(mail.outbox) == 1


def test_admin_booking_respects_double_booking_protection(admin_client, slot, booking):
    assert admin_client.post(ADMIN_BOOKINGS_URL, body(slot), format="json").status_code == 409


def test_admin_can_filter_and_search_bookings(admin_client, booking):
    date = booking.slot.date.isoformat()
    assert admin_client.get(f"{ADMIN_BOOKINGS_URL}?date={date}").data["data"]["count"] == 1
    assert admin_client.get(f"{ADMIN_BOOKINGS_URL}?source=USER").data["data"]["count"] == 1
    assert admin_client.get(f"{ADMIN_BOOKINGS_URL}?source=ADMIN").data["data"]["count"] == 0
    assert admin_client.get(
        f"{ADMIN_BOOKINGS_URL}?booking_reference={booking.booking_reference}"
    ).data["data"]["count"] == 1
    assert admin_client.get(
        f"{ADMIN_BOOKINGS_URL}?search={booking.email}").data["data"]["count"] == 1


def test_admin_can_update_and_complete_booking(admin_client, booking):
    response = admin_client.patch(f"{ADMIN_BOOKINGS_URL}{booking.id}/",
                                  {"status": BookingStatus.COMPLETED}, format="json")
    assert response.status_code == 200
    booking.refresh_from_db()
    assert booking.status == BookingStatus.COMPLETED


def test_admin_can_cancel_booking(admin_client, booking):
    assert admin_client.delete(f"{ADMIN_BOOKINGS_URL}{booking.id}/").status_code == 200
    booking.refresh_from_db()
    assert booking.status == BookingStatus.CANCELLED


def test_booking_reference_is_unique_and_sequential(user, slot, second_slot):
    first = create_booking(slot_id=slot.id, full_name="A B", email="a@example.com",
                           phone_number="9800000021", user=user)
    second = create_booking(slot_id=second_slot.id, full_name="C D", email="c@example.com",
                            phone_number="9800000022", user=user)
    assert first.booking_reference != second.booking_reference
    assert second.booking_reference.endswith("0002")
