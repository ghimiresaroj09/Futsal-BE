"""Booking business logic: atomic, concurrency-safe."""
from __future__ import annotations

import logging
import datetime as dt
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import Max, Q
from django.conf import settings
from django.utils import timezone

from bookings.models import ACTIVE_BOOKING_STATUSES, Booking
from bookings.state_machine import (
    CANCELLABLE_STATUSES, RESCHEDULABLE_STATUSES, assert_transition,
)
from common.enums import (
    BookingSource, BookingStatus, PaymentMethod, PaymentStatus, SlotStatus,
)
from common.exceptions import ConflictError, ServiceError, SlotUnavailableError
from common.utils import local_now
from futsal.models import FutsalClosure, Slot
from notifications.emails import (
    send_booking_cancellation_email, send_booking_confirmation_email, send_reschedule_email,
)
from notifications.services import (
    create_admin_booking_cancellation_notifications, create_admin_booking_notifications,
)
from payments.models import Payment
from payments.services import create_payment_for_booking, refund_payment

logger = logging.getLogger("futsal.bookings")


def generate_booking_reference(slot: Slot) -> str:
    """FSL-YYYYMMDD-0001, sequential per slot date."""
    prefix = f"{settings.BOOKING_REFERENCE_PREFIX}-{slot.date.strftime('%Y%m%d')}"
    last = (
        Booking.objects.filter(booking_reference__startswith=prefix)
        .aggregate(m=Max("booking_reference"))["m"]
    )
    sequence = int(last.split("-")[-1]) + 1 if last else 1
    return f"{prefix}-{sequence:04d}"


def _lock_slot(slot_id) -> Slot:
    slot = (
        Slot.objects.select_for_update()
        .select_related("futsal")
        .filter(pk=slot_id)
        .first()
    )
    if slot is None:
        raise ServiceError("Slot not found.", errors={"slot_id": ["Slot not found."]},
                           code="not_found")
    return slot


def _assert_bookable(slot: Slot) -> None:
    closure = FutsalClosure.objects.filter(futsal_id=slot.futsal_id, date=slot.date).first()
    if closure is not None:
        message = "The futsal is closed on this date."
        if closure.reason:
            message = f"{message} ({closure.reason})"
        raise ConflictError(message, errors={"date": [message]})
    if slot.status == SlotStatus.BLOCKED:
        raise ConflictError("Slot is blocked.", errors={"slot": ["Slot is blocked."]})
    if slot.status != SlotStatus.AVAILABLE:
        raise SlotUnavailableError(errors={"slot": ["Slot is already booked."]})
    if slot.is_past:
        raise ServiceError("Slot is in the past.", errors={"slot": ["Slot is in the past."]})
    if Booking.objects.filter(slot=slot, status__in=ACTIVE_BOOKING_STATUSES).exists():
        raise SlotUnavailableError(errors={"slot": ["Slot is already booked."]})


@transaction.atomic
def create_booking(
    *, slot_id, full_name: str, email: str, phone_number: str,
    user=None, created_by=None, source: str = BookingSource.USER,
    payment_method: str = PaymentMethod.CASH, payment_status: str = PaymentStatus.PENDING,
    advance_amount: Decimal | None = None, status: str = BookingStatus.CONFIRMED, notes: str = "",
) -> Booking:
    """Create a booking atomically. Raises 409 ConflictError on double booking."""
    slot = _lock_slot(slot_id)
    _assert_bookable(slot)

    if user is not None and Booking.objects.filter(
        slot=slot, user=user, status__in=ACTIVE_BOOKING_STATUSES
    ).exists():
        raise ConflictError("You have already booked this slot.",
                            errors={"slot": ["Duplicate booking."]})

    amount: Decimal = slot.effective_price
    try:
        booking = Booking.objects.create(
            booking_reference=generate_booking_reference(slot),
            user=user,
            futsal=slot.futsal,
            slot=slot,
            full_name=full_name.strip(),
            email=email.lower().strip(),
            phone_number=phone_number.strip(),
            amount=amount,
            status=status,
            booking_source=source,
            created_by=created_by or user,
            notes=notes,
        )
    except IntegrityError as exc:
        logger.warning("Double booking prevented slot=%s: %s", slot_id, exc)
        raise SlotUnavailableError(errors={"slot": ["Slot is already booked."]})

    Slot.objects.filter(pk=slot.pk).update(status=SlotStatus.BOOKED)
    slot.status = SlotStatus.BOOKED

    create_payment_for_booking(
        booking=booking, amount=amount, method=payment_method, status=payment_status,
        advance_amount=advance_amount,
    )
    logger.info("Booking created reference=%s slot=%s source=%s",
                booking.booking_reference, slot.pk, source)
    if source == BookingSource.USER:
        create_admin_booking_notifications(booking=booking)
    # Creating a request never emails the customer. The confirmation email is
    # sent only when an administrator explicitly changes its status to confirmed.
    return booking


def _safe_email(fn, *args) -> None:
    try:
        fn(*args)
    except Exception:  # pragma: no cover - email must never break the transaction
        logger.exception("Email delivery failed for %s", fn.__name__)


@transaction.atomic
def cancel_booking(*, booking: Booking, actor=None, reason: str = "") -> Booking:
    booking = Booking.objects.select_for_update().select_related("slot").get(pk=booking.pk)
    if booking.status not in CANCELLABLE_STATUSES:
        assert_transition(booking.status, BookingStatus.CANCELLED)
    assert_transition(booking.status, BookingStatus.CANCELLED)

    booking.status = BookingStatus.CANCELLED
    booking.cancelled_at = timezone.now()
    booking.cancellation_reason = reason
    booking.save(update_fields=["status", "cancelled_at", "cancellation_reason", "updated_at"])

    Slot.objects.filter(pk=booking.slot_id, status=SlotStatus.BOOKED).update(
        status=SlotStatus.AVAILABLE
    )
    payment = Payment.objects.filter(booking=booking).first()
    if payment:
        refund_payment(payment)
    logger.info("Booking cancelled reference=%s actor=%s", booking.booking_reference,
                getattr(actor, "id", None))
    # A cancellation is always operationally relevant to admins, regardless of
    # whether it was initiated by the customer or an admin.
    create_admin_booking_cancellation_notifications(booking=booking)
    transaction.on_commit(lambda: _safe_email(send_booking_cancellation_email, booking, reason))
    return booking


@transaction.atomic
def reschedule_booking(*, booking: Booking, new_slot_id, actor=None) -> Booking:
    """Atomically move a booking to a new slot. Rolls back completely on failure."""
    booking = (
        Booking.objects.select_for_update().select_related("slot", "futsal").get(pk=booking.pk)
    )
    if booking.status not in RESCHEDULABLE_STATUSES:
        raise ServiceError(
            "You cannot reschedule this booking.",
            errors={"booking": ["This booking is no longer eligible for rescheduling."]},
        )
    old_slot = booking.slot
    if str(old_slot.pk) == str(new_slot_id):
        raise ServiceError("New slot must be different from the current slot.",
                           errors={"new_slot_id": ["New slot must be different."]})

    new_slot = _lock_slot(new_slot_id)
    _assert_bookable(new_slot)

    booking.slot = new_slot
    booking.futsal = new_slot.futsal
    booking.rescheduled_from = old_slot
    booking.status = BookingStatus.RESCHEDULED
    try:
        booking.save(update_fields=["slot", "futsal", "rescheduled_from", "status", "updated_at"])
    except IntegrityError:
        raise SlotUnavailableError(errors={"slot": ["Slot is already booked."]})

    Slot.objects.filter(pk=new_slot.pk).update(status=SlotStatus.BOOKED)
    Slot.objects.filter(pk=old_slot.pk).update(status=SlotStatus.AVAILABLE)

    logger.info("Booking rescheduled reference=%s old_slot=%s new_slot=%s",
                booking.booking_reference, old_slot.pk, new_slot.pk)
    old_slot.refresh_from_db()
    transaction.on_commit(lambda: _safe_email(send_reschedule_email, booking, old_slot))
    return booking


@transaction.atomic
def change_booking_status(*, booking: Booking, new_status: str, actor=None,
                          reason: str = "") -> Booking:
    if new_status == BookingStatus.CANCELLED:
        return cancel_booking(booking=booking, actor=actor, reason=reason)
    assert_transition(booking.status, new_status)
    booking.status = new_status
    booking.save(update_fields=["status", "updated_at"])
    if new_status == BookingStatus.CONFIRMED:
        transaction.on_commit(lambda: _safe_email(send_booking_confirmation_email, booking))
    if new_status == BookingStatus.COMPLETED:
        payment = Payment.objects.filter(booking=booking).first()
        if payment and payment.payment_status in {PaymentStatus.PENDING, PaymentStatus.ADVANCED}:
            from payments.services import mark_paid

            mark_paid(payment)
    logger.info("Booking status changed reference=%s status=%s",
                booking.booking_reference, new_status)
    return booking


def mark_completed(*, booking: Booking, actor=None) -> Booking:
    return change_booking_status(booking=booking, new_status=BookingStatus.COMPLETED, actor=actor)


@transaction.atomic
def complete_expired_bookings(*, now: dt.datetime | None = None) -> int:
    """Complete bookings whose local slot end time has passed.

    This is intentionally idempotent so it can safely run from both Celery Beat
    and the HTTP cron fallback.  A pending booking can expire before an admin
    acts on it, so all unfinished booking states are included.
    """
    now = now or local_now()
    completable_statuses = [
        BookingStatus.PENDING,
        BookingStatus.CONFIRMED,
        BookingStatus.RESCHEDULED,
    ]
    expired = (
        Booking.objects.select_for_update()
        .select_related("payment", "slot")
        .filter(status__in=completable_statuses)
        .filter(Q(slot__date__lt=now.date()) | Q(
            slot__date=now.date(), slot__end_time__lt=now.time()
        ))
    )

    completed = 0
    for booking in expired:
        booking.status = BookingStatus.COMPLETED
        booking.save(update_fields=["status", "updated_at"])
        if booking.payment.payment_status in {PaymentStatus.PENDING, PaymentStatus.ADVANCED}:
            from payments.services import mark_paid

            mark_paid(booking.payment)
        completed += 1

    logger.info("complete_expired_bookings completed=%d", completed)
    return completed
