"""Booking model with database-enforced one-active-booking-per-slot rule."""
from __future__ import annotations

from django.db import models

from common.enums import BookingSource, BookingStatus
from common.models import BaseModel

ACTIVE_BOOKING_STATUSES = [
    BookingStatus.PENDING,
    BookingStatus.CONFIRMED,
    BookingStatus.COMPLETED,
]


class BookingQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status__in=ACTIVE_BOOKING_STATUSES)

    def for_user(self, user):
        return self.filter(user=user)


class Booking(BaseModel):
    booking_reference = models.CharField(max_length=32, unique=True, db_index=True)
    user = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="bookings",
    )
    futsal = models.ForeignKey("futsal.Futsal", on_delete=models.PROTECT, related_name="bookings")
    slot = models.ForeignKey("futsal.Slot", on_delete=models.PROTECT, related_name="bookings")

    # Contact details snapshotted at booking time (profile may change later).
    full_name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True)
    phone_number = models.CharField(max_length=20, db_index=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=12, choices=BookingStatus.choices,
        default=BookingStatus.PENDING, db_index=True,
    )
    booking_source = models.CharField(
        max_length=6, choices=BookingSource.choices,
        default=BookingSource.USER, db_index=True,
    )
    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="created_bookings",
    )
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.CharField(max_length=255, blank=True, default="")
    rescheduled_from = models.ForeignKey(
        "futsal.Slot", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="rescheduled_bookings",
    )
    notes = models.TextField(blank=True, default="")

    objects = BookingQuerySet.as_manager()

    class Meta:
        db_table = "bookings_booking"
        ordering = ["-created_at"]
        constraints = [
            # DB-level guarantee: a slot can only have ONE active booking.
            models.UniqueConstraint(
                fields=["slot"],
                condition=models.Q(status__in=ACTIVE_BOOKING_STATUSES),
                name="uniq_active_booking_per_slot",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["booking_source"]),
        ]

    def __str__(self) -> str:
        return self.booking_reference

    @property
    def is_active(self) -> bool:
        return self.status in ACTIVE_BOOKING_STATUSES
