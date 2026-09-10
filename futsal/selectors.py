"""Slot query helpers."""
from __future__ import annotations

from django.db.models import Prefetch

from futsal.models import Slot


def slots_queryset():
    from bookings.models import Booking
    return Slot.objects.select_related("futsal").prefetch_related(
        Prefetch(
            "bookings",
            queryset=Booking.objects.filter(status__in=["PENDING", "CONFIRMED", "COMPLETED"]),
            to_attr="active_bookings"
        )
    )
