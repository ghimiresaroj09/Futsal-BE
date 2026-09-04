"""Booking query helpers."""
from __future__ import annotations

from bookings.models import Booking


def bookings_queryset():
    return Booking.objects.select_related("slot", "futsal", "user", "payment")


def user_bookings(user):
    return bookings_queryset().filter(user=user)
