"""Payment services."""
from __future__ import annotations

import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from common.enums import PaymentStatus
from payments.models import Payment

logger = logging.getLogger("futsal.payments")


@transaction.atomic
def create_payment_for_booking(*, booking, amount: Decimal, method: str,
                               status: str = PaymentStatus.PENDING) -> Payment:
    return Payment.objects.create(
        booking=booking,
        amount=amount,
        payment_method=method,
        payment_status=status,
        paid_at=timezone.now() if status == PaymentStatus.PAID else None,
    )


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
    """Refund a paid payment; pending payments simply fail out of revenue."""
    if payment.payment_status == PaymentStatus.PAID:
        payment.refunded_amount = payment.amount
        payment.payment_status = PaymentStatus.REFUNDED
        payment.save(update_fields=["refunded_amount", "payment_status", "updated_at"])
        logger.info("Payment refunded booking=%s amount=%s", payment.booking_id, payment.amount)
    return payment
