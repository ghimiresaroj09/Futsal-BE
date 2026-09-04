"""Reminder services."""
from __future__ import annotations

import datetime as dt
import logging

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from bookings.models import Booking
from common.enums import BookingStatus, ReminderStatus, ReminderType
from common.exceptions import EmailDeliveryError
from common.utils import combine_local
from notifications.emails import send_booking_reminder_email
from notifications.models import Reminder

logger = logging.getLogger("futsal.reminders")

REMINDER_ELIGIBLE_STATUSES = [BookingStatus.PENDING, BookingStatus.CONFIRMED,
                              BookingStatus.RESCHEDULED]


def upcoming_bookings_needing_reminder(now: dt.datetime | None = None):
    """Bookings starting within [lead, lead+window) minutes that have no automatic reminder."""
    now = now or timezone.now()
    lead = dt.timedelta(minutes=settings.REMINDER_LEAD_MINUTES)
    window = dt.timedelta(minutes=settings.REMINDER_WINDOW_MINUTES)
    target_from = now + lead - window
    target_to = now + lead

    candidates = (
        Booking.objects.select_related("slot", "futsal")
        .filter(status__in=REMINDER_ELIGIBLE_STATUSES,
                slot__date__in=[(target_from).date(), target_to.date()])
        .exclude(reminders__reminder_type=ReminderType.AUTOMATIC_ONE_HOUR)
    )
    return [
        booking
        for booking in candidates
        if target_from <= combine_local(booking.slot.date, booking.slot.start_time) <= target_to
    ]


def _deliver(reminder: Reminder, booking: Booking) -> Reminder:
    try:
        send_booking_reminder_email(booking)
    except Exception as exc:  # noqa: BLE001
        reminder.status = ReminderStatus.FAILED
        reminder.error_message = str(exc)[:1000]
        reminder.save(update_fields=["status", "error_message", "updated_at"])
        logger.error("Reminder delivery failed booking=%s error=%s",
                     booking.booking_reference, exc)
        raise EmailDeliveryError(
            "Reminder email could not be delivered.",
            errors={"email": [str(exc)[:200]]},
        )
    reminder.status = ReminderStatus.SENT
    reminder.sent_at = timezone.now()
    reminder.error_message = ""
    reminder.save(update_fields=["status", "sent_at", "error_message", "updated_at"])
    logger.info("Reminder sent booking=%s type=%s", booking.booking_reference,
                reminder.reminder_type)
    return reminder


def send_automatic_reminder(*, booking: Booking) -> Reminder | None:
    """Create-and-send the one-hour reminder. Duplicates are prevented at DB level."""
    scheduled_at = combine_local(booking.slot.date, booking.slot.start_time) - dt.timedelta(
        minutes=settings.REMINDER_LEAD_MINUTES
    )
    try:
        with transaction.atomic():
            reminder = Reminder.objects.create(
                booking=booking,
                reminder_type=ReminderType.AUTOMATIC_ONE_HOUR,
                scheduled_at=scheduled_at,
            )
    except IntegrityError:
        logger.info("Duplicate automatic reminder skipped booking=%s", booking.pk)
        return None
    try:
        return _deliver(reminder, booking)
    except EmailDeliveryError:
        return reminder


def send_manual_reminder(*, booking: Booking, actor=None) -> Reminder:
    """Admin-triggered reminder. Errors are surfaced, never silently swallowed."""
    reminder = Reminder.objects.create(
        booking=booking,
        reminder_type=ReminderType.MANUAL,
        scheduled_at=timezone.now(),
        triggered_by=actor,
    )
    return _deliver(reminder, booking)
