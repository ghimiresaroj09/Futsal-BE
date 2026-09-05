"""Revenue aggregation queries."""
from __future__ import annotations

import datetime as dt
from decimal import Decimal

from django.db.models import Count, DecimalField, F, Q, Sum, Value
from django.db.models.functions import Coalesce, TruncMonth, TruncWeek

from common.enums import BookingStatus, PaymentStatus
from payments.models import Payment

_MONEY = DecimalField(max_digits=14, decimal_places=2)


def _zero():
    return Value(Decimal("0.00"), output_field=_MONEY)


def payments_in_range(start: dt.date | None = None, end: dt.date | None = None,
                      payment_status: str | None = None, futsal_id=None):
    qs = Payment.objects.select_related("booking", "booking__slot")
    if start:
        qs = qs.filter(booking__slot__date__gte=start)
    if end:
        qs = qs.filter(booking__slot__date__lte=end)
    if payment_status:
        qs = qs.filter(payment_status=payment_status)
    if futsal_id:
        qs = qs.filter(booking__futsal_id=futsal_id)
    return qs


def revenue_summary(start=None, end=None, payment_status=None, futsal_id=None) -> dict:
    qs = payments_in_range(start, end, payment_status, futsal_id)
    agg = qs.aggregate(
        total_revenue=Coalesce(
            Sum("amount", filter=Q(payment_status=PaymentStatus.PAID)), _zero()
        ),
        refunded_amount=Coalesce(Sum("refunded_amount"), _zero()),
        number_of_bookings=Count("id"),
        paid_bookings=Count("id", filter=Q(payment_status=PaymentStatus.PAID)),
        cancelled_bookings=Count("id", filter=Q(booking__status=BookingStatus.CANCELLED)),
    )
    agg["net_revenue"] = agg["total_revenue"]
    return agg


# `date` is already a DateField, so "day" needs no truncation function.
_TRUNC = {"week": TruncWeek, "month": TruncMonth}


def revenue_series(period: str = "day", start=None, end=None, futsal_id=None) -> list[dict]:
    trunc = _TRUNC.get(period)
    qs = payments_in_range(start, end, PaymentStatus.PAID, futsal_id)
    bucket = trunc("booking__slot__date") if trunc else F("booking__slot__date")
    rows = (
        qs.annotate(bucket=bucket)
        .values("bucket")
        .annotate(revenue=Coalesce(Sum("amount"), _zero()))
        .order_by("bucket")
    )
    return [
        {"date": row["bucket"].isoformat() if row["bucket"] else None,
         "revenue": row["revenue"]}
        for row in rows
    ]
