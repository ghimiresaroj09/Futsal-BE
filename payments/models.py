"""Payment / revenue records."""
from __future__ import annotations

from django.core.validators import MinValueValidator
from django.db import models

from common.enums import PaymentMethod, PaymentStatus
from common.models import BaseModel


class Payment(BaseModel):
    """Financial record for a booking.

    `amount` is stored at booking/payment time so historical revenue is
    unaffected by later futsal price changes.
    """

    booking = models.OneToOneField(
        "bookings.Booking", on_delete=models.CASCADE, related_name="payment"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=10, choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING, db_index=True,
    )
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH
    )
    transaction_reference = models.CharField(max_length=100, blank=True, default="", db_index=True)
    paid_at = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        db_table = "payments_payment"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gte=0),
                                   name="payment_amount_non_negative"),
        ]
        indexes = [models.Index(fields=["payment_status", "paid_at"])]

    def __str__(self) -> str:
        return f"Payment({self.booking_id}, {self.amount}, {self.payment_status})"
