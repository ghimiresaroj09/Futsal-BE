"""Reminder tracking."""
from __future__ import annotations

from django.db import models

from common.enums import ReminderStatus, ReminderType
from common.models import BaseModel


class Reminder(BaseModel):
    booking = models.ForeignKey(
        "bookings.Booking", on_delete=models.CASCADE, related_name="reminders"
    )
    reminder_type = models.CharField(
        max_length=32, choices=ReminderType.choices, db_index=True
    )
    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=ReminderStatus.choices,
        default=ReminderStatus.PENDING, db_index=True,
    )
    error_message = models.TextField(blank=True, default="")
    triggered_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, blank=True, null=True,
        related_name="triggered_reminders",
    )

    class Meta:
        db_table = "notifications_reminder"
        ordering = ["-created_at"]
        constraints = [
            # Only ONE automatic one-hour reminder may ever exist per booking.
            models.UniqueConstraint(
                fields=["booking", "reminder_type"],
                condition=models.Q(reminder_type=ReminderType.AUTOMATIC_ONE_HOUR),
                name="uniq_automatic_reminder_per_booking",
            )
        ]
        indexes = [models.Index(fields=["status", "scheduled_at"])]

    def __str__(self) -> str:
        return f"Reminder({self.booking_id}, {self.reminder_type}, {self.status})"
