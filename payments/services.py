"""Payment services."""
from __future__ import annotations

import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from common.enums import PaymentStatus
from common.exceptions import ServiceError
from payments.models import Payment

logger = logging.getLogger("futsal.payments")


@transaction.atomic
def create_payment_for_booking(*, booking, amount: Decimal, method: str,
                               status: str = PaymentStatus.PENDING,
                               advance_amount: Decimal | None = None) -> Payment:
    advance_amount = advance_amount or Decimal("0.00")
    _validate_advance_amount(advance_amount, amount)
    if advance_amount > 0:
        status = PaymentStatus.ADVANCED
    return Payment.objects.create(
        booking=booking,
        amount=amount,
        payment_method=method,
        payment_status=status,
        advance_amount=advance_amount,
        paid_at=timezone.now() if status == PaymentStatus.PAID else None,
    )


def _validate_advance_amount(advance_amount: Decimal, amount: Decimal) -> None:
    if advance_amount < 0 or advance_amount > amount:
        raise ServiceError(
            "Advance amount must be between zero and the booking amount.",
            errors={"advance_amount": ["Must not exceed the booking amount."]},
        )


@transaction.atomic
def update_payment_details(*, payment: Payment, advance_amount: Decimal | None = None,
                           payment_method: str | None = None) -> Payment:
    """Update admin-managed payment details without reopening paid/refunded payments."""
    update_fields = []
    if advance_amount is not None:
        _validate_advance_amount(advance_amount, payment.amount)
        payment.advance_amount = advance_amount
        update_fields.append("advance_amount")
        if payment.payment_status not in {PaymentStatus.PAID, PaymentStatus.REFUNDED}:
            payment.payment_status = (
                PaymentStatus.ADVANCED if advance_amount > 0 else PaymentStatus.PENDING
            )
            update_fields.append("payment_status")
    if payment_method is not None:
        payment.payment_method = payment_method
        update_fields.append("payment_method")
    if update_fields:
        payment.save(update_fields=[*update_fields, "updated_at"])
    return payment


@transaction.atomic
def mark_paid(payment: Payment, *, transaction_reference: str = "") -> Payment:
    payment.payment_status = PaymentStatus.PAID
    payment.paid_at = timezone.now()
    if transaction_reference:
        payment.transaction_reference = transaction_reference
    payment.save(update_fields=["payment_status", "paid_at", "transaction_reference", "updated_at"])
    return payment


@transaction.atomic
def refund_payment(payment: Payment) -> Payment:
    """Mark cancelled bookings as refunded, refunding what has actually been collected."""
    if payment.payment_status == PaymentStatus.REFUNDED:
        return payment
    payment.refunded_amount = (
        payment.amount if payment.payment_status == PaymentStatus.PAID else payment.advance_amount
    )
    payment.payment_status = PaymentStatus.REFUNDED
    payment.save(update_fields=["refunded_amount", "payment_status", "updated_at"])
    logger.info("Payment refunded booking=%s amount=%s", payment.booking_id, payment.refunded_amount)
    return payment
