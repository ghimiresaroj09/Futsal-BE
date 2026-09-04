"""Dashboard aggregations."""
from __future__ import annotations

import datetime as dt
from decimal import Decimal

from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce, TruncMonth, TruncWeek

from bookings.models import Booking
from common.enums import BookingStatus, PaymentStatus, SlotStatus
from common.utils import local_today
from futsal.models import Slot
from payments.models import Payment

ZERO = Decimal("0.00")


def today_overview(today: dt.date | None = None) -> dict:
    today = today or local_today()
    bookings = Booking.objects.filter(slot__date=today)
    slots = Slot.objects.filter(date=today)
    revenue = Payment.objects.filter(
        booking__slot__date=today, payment_status=PaymentStatus.PAID
    ).aggregate(total=Coalesce(Sum("amount"), ZERO))["total"]

    counts = bookings.aggregate(
        total=Count("id"),
        completed=Count("id", filter=Q(status=BookingStatus.COMPLETED)),
        cancelled=Count("id", filter=Q(status=BookingStatus.CANCELLED)),
    )
    slot_counts = slots.aggregate(
        available=Count("id", filter=Q(status=SlotStatus.AVAILABLE)),
        booked=Count("id", filter=Q(status=SlotStatus.BOOKED)),
        blocked=Count("id", filter=Q(status=SlotStatus.BLOCKED)),
    )
    return {
        "date": today.isoformat(),
        "revenue": revenue,
        "bookings": counts["total"],
        "available_slots": slot_counts["available"],
        "booked_slots": slot_counts["booked"],
        "blocked_slots": slot_counts["blocked"],
        "completed_bookings": counts["completed"],
        "cancelled_bookings": counts["cancelled"],
    }


def slot_analytics(start: dt.date | None = None, end: dt.date | None = None) -> dict:
    qs = Slot.objects.all()
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    data = qs.aggregate(
        available=Count("id", filter=Q(status=SlotStatus.AVAILABLE)),
        booked=Count("id", filter=Q(status=SlotStatus.BOOKED)),
        blocked=Count("id", filter=Q(status=SlotStatus.BLOCKED)),
        total=Count("id"),
    )
    bookable = data["available"] + data["booked"]
    data["occupancy_rate"] = round(data["booked"] / bookable * 100, 2) if bookable else 0.0
    return data


_TRUNC = {"week": TruncWeek, "month": TruncMonth}


def bookings_series(period: str = "day", start=None, end=None) -> list[dict]:
    trunc = _TRUNC.get(period)
    qs = Booking.objects.all()
    if start:
        qs = qs.filter(slot__date__gte=start)
    if end:
        qs = qs.filter(slot__date__lte=end)
    rows = (
        qs.annotate(bucket=trunc("slot__date") if trunc else F("slot__date"))
        .values("bucket")
        .annotate(
            bookings=Count("id"),
            confirmed=Count("id", filter=Q(status=BookingStatus.CONFIRMED)),
            cancelled=Count("id", filter=Q(status=BookingStatus.CANCELLED)),
            completed=Count("id", filter=Q(status=BookingStatus.COMPLETED)),
        )
        .order_by("bucket")
    )
    return [
        {
            "date": row["bucket"].isoformat() if row["bucket"] else None,
            "bookings": row["bookings"],
            "confirmed": row["confirmed"],
            "cancelled": row["cancelled"],
            "completed": row["completed"],
        }
        for row in rows
    ]
