"""Booking state machine.

Allowed transitions::

    PENDING     -> CONFIRMED, CANCELLED
    CONFIRMED   -> COMPLETED, CANCELLED, RESCHEDULED
    RESCHEDULED -> CONFIRMED, COMPLETED, CANCELLED
    COMPLETED   -> (terminal)
    CANCELLED   -> (terminal)
"""
from __future__ import annotations

from common.enums import BookingStatus
from common.exceptions import InvalidStateTransition

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    BookingStatus.PENDING: {BookingStatus.CONFIRMED, BookingStatus.CANCELLED},
    BookingStatus.CONFIRMED: {
        BookingStatus.COMPLETED, BookingStatus.CANCELLED, BookingStatus.RESCHEDULED,
    },
    BookingStatus.RESCHEDULED: {
        BookingStatus.CONFIRMED, BookingStatus.COMPLETED, BookingStatus.CANCELLED,
    },
    BookingStatus.COMPLETED: set(),
    BookingStatus.CANCELLED: set(),
}

RESCHEDULABLE_STATUSES = {BookingStatus.PENDING, BookingStatus.CONFIRMED,
                          BookingStatus.RESCHEDULED}
CANCELLABLE_STATUSES = {BookingStatus.PENDING, BookingStatus.CONFIRMED,
                        BookingStatus.RESCHEDULED}


def can_transition(current: str, new: str) -> bool:
    return new in ALLOWED_TRANSITIONS.get(current, set())


def assert_transition(current: str, new: str) -> None:
    if current == new:
        raise InvalidStateTransition(
            f"Booking is already {current}.",
            errors={"status": [f"Booking is already {current}."]},
        )
    if not can_transition(current, new):
        raise InvalidStateTransition(
            f"Cannot change booking status from {current} to {new}.",
            errors={"status": [f"Cannot change booking status from {current} to {new}."]},
        )
