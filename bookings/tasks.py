"""Periodic tasks for booking lifecycle maintenance."""
from __future__ import annotations

from celery import shared_task

from bookings.services import complete_expired_bookings


@shared_task(name="bookings.complete_expired_bookings")
def complete_expired_bookings_task() -> int:
    """Mark every booking whose slot has ended as completed."""
    return complete_expired_bookings()
