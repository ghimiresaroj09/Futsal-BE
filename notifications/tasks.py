"""Celery tasks for reminders."""
from __future__ import annotations

import logging

from celery import shared_task

from notifications.services import send_automatic_reminder, upcoming_bookings_needing_reminder

logger = logging.getLogger("futsal.reminders")


@shared_task(name="notifications.dispatch_due_reminders")
def dispatch_due_reminders() -> int:
    """Periodic task: send one-hour reminders for upcoming bookings."""
    bookings = upcoming_bookings_needing_reminder()
    sent = 0
    for booking in bookings:
        reminder = send_automatic_reminder(booking=booking)
        if reminder is not None:
            sent += 1
    logger.info("dispatch_due_reminders processed=%d", sent)
    return sent


@shared_task(name="notifications.send_reminder_for_booking")
def send_reminder_for_booking(booking_id: str) -> bool:
    from bookings.models import Booking

    booking = Booking.objects.select_related("slot", "futsal").filter(pk=booking_id).first()
    if booking is None:
        return False
    return send_automatic_reminder(booking=booking) is not None
