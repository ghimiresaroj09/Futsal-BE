"""Reminder services."""
from __future__ import annotations

import datetime as dt
import logging

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from bookings.models import Booking
from accounts.models import User
from common.enums import UserRole
from common.enums import BookingStatus, ReminderStatus, ReminderType
from common.exceptions import EmailDeliveryError
from common.utils import combine_local
from notifications.emails import send_booking_reminder_email
from notifications.models import AdminNotification, Reminder


def _ordinal_day(day: int) -> str:
    if 10 < day % 100 < 14:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix}"


def _format_slot_time(value: dt.time) -> str:
    hour = value.hour % 12 or 12
    minute = f":{value.minute:02d}" if value.minute else ""
    meridiem = "am" if value.hour < 12 else "pm"
    return f"{hour}{minute} {meridiem}"


def booking_slot_description(booking: Booking) -> str:
    """Return a concise, human-friendly description for an in-app event."""
    slot = booking.slot
    start = _format_slot_time(slot.start_time)
    end = _format_slot_time(slot.end_time)
    # Avoid repeating the same meridiem: "6 - 7 am", not "6 am - 7 am".
    start_time, start_meridiem = start.rsplit(" ", 1)
    end_time, end_meridiem = end.rsplit(" ", 1)
    time_range = (
        f"{start_time} - {end_time} {end_meridiem}"
        if start_meridiem == end_meridiem
        else f"{start} - {end}"
    )
    date = slot.date
    return f"{time_range} on {_ordinal_day(date.day)} {date.strftime('%B')}"


def _create_admin_booking_notifications(*, booking: Booking, title: str, message: str) -> int:
    """Create one unread booking-event notification for each active administrator."""
    recipients = User.objects.filter(role=UserRole.ADMIN, is_active=True).only("id")
    notifications = [
        AdminNotification(
            recipient=admin, booking=booking, title=title, message=message,
        )
        for admin in recipients
    ]
    AdminNotification.objects.bulk_create(notifications)
    return len(notifications)


def create_admin_booking_notifications(*, booking: Booking) -> int:
    """Notify admins that a customer created a booking."""
    return _create_admin_booking_notifications(
        booking=booking,
        title="New booking",
        message=f"{booking.full_name} booked a slot for {booking_slot_description(booking)}.",
    )


def create_admin_booking_cancellation_notifications(*, booking: Booking) -> int:
    """Notify admins that a booking was cancelled."""
    return _create_admin_booking_notifications(
        booking=booking,
        title="Booking cancelled",
        message=(
            f"{booking.full_name} cancelled their booking for "
            f"{booking_slot_description(booking)}."
        ),
    )

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
