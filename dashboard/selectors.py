"""Dashboard aggregations."""
from __future__ import annotations

import datetime as dt
from decimal import Decimal

from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce, TruncMonth, TruncWeek
from django.utils import timezone

from bookings.models import Booking
from common.enums import BookingSource, BookingStatus, PaymentStatus, SlotStatus
from common.utils import local_today
from futsal.models import Slot
from payments.models import Payment

ZERO = Decimal("0.00")


def analytics(start: dt.date, end: dt.date, *, period: str, futsal_id=None) -> dict:
    """Return the complete analytics dashboard payload for a reporting range."""
    booking_filters = Q(slot__date__gte=start, slot__date__lte=end)
    payment_filters = Q(booking__slot__date__gte=start, booking__slot__date__lte=end, payment_status=PaymentStatus.PAID)
    if futsal_id:
        booking_filters &= Q(futsal_id=futsal_id)
        payment_filters &= Q(booking__futsal_id=futsal_id)
    bookings, payments = Booking.objects.filter(booking_filters), Payment.objects.filter(payment_filters)
    revenue = payments.aggregate(total=Coalesce(Sum("amount"), ZERO))["total"]
    booking_count, revenue_booking_count = bookings.count(), payments.count()
    average = revenue / revenue_booking_count if revenue_booking_count else ZERO
    previous_end = start - dt.timedelta(days=1)
    previous_start = previous_end - dt.timedelta(days=(end - start).days)
    previous_booking_filters = Q(slot__date__gte=previous_start, slot__date__lte=previous_end)
    previous_payment_filters = Q(booking__slot__date__gte=previous_start, booking__slot__date__lte=previous_end, payment_status=PaymentStatus.PAID)
    if futsal_id:
        previous_booking_filters &= Q(futsal_id=futsal_id)
        previous_payment_filters &= Q(booking__futsal_id=futsal_id)
    previous_bookings, previous_payments = Booking.objects.filter(previous_booking_filters), Payment.objects.filter(previous_payment_filters)
    previous_revenue = previous_payments.aggregate(total=Coalesce(Sum("amount"), ZERO))["total"]
    previous_payment_count = previous_payments.count()
    previous_average = previous_revenue / previous_payment_count if previous_payment_count else ZERO

    def change(current, previous):
        return round(float((current - previous) / previous * 100), 1) if previous else 0.0

    status_counts = dict(bookings.values("status").annotate(count=Count("id")).values_list("status", "count"))
    breakdown = [{"status": status, "label": BookingStatus(status).label, "count": status_counts.get(status, 0), "percentage": round(status_counts.get(status, 0) / booking_count * 100, 1) if booking_count else 0} for status, _ in BookingStatus.choices]
    by_day = {row["slot__date"].weekday(): row["count"] for row in bookings.values("slot__date").annotate(count=Count("id"))}
    weekdays = [("MONDAY", "Mon"), ("TUESDAY", "Tue"), ("WEDNESDAY", "Wed"), ("THURSDAY", "Thu"), ("FRIDAY", "Fri"), ("SATURDAY", "Sat"), ("SUNDAY", "Sun")]
    truncate = None if period in {"7d", "30d"} else TruncMonth
    rows = (payments.annotate(bucket=F("booking__slot__date") if truncate is None else truncate("booking__slot__date")).values("bucket").annotate(revenue=Coalesce(Sum("amount"), ZERO), booking_count=Count("id")).order_by("bucket"))
    overview = [{"period": row["bucket"].isoformat() if truncate is None else row["bucket"].strftime("%Y-%m"), "label": row["bucket"].strftime("%d %b") if truncate is None else row["bucket"].strftime("%b"), "revenue": row["revenue"], "booking_count": row["booking_count"]} for row in rows]
    source_rows = {row["booking__booking_source"]: row for row in payments.values("booking__booking_source").annotate(revenue=Coalesce(Sum("amount"), ZERO), booking_count=Count("id"))}
    sources = [{"source": source, "label": "User bookings" if source == BookingSource.USER else "Admin bookings", "revenue": source_rows.get(source, {}).get("revenue", ZERO), "booking_count": source_rows.get(source, {}).get("booking_count", 0), "percentage": round(float(source_rows.get(source, {}).get("revenue", ZERO) / revenue * 100), 1) if revenue else 0} for source, _ in BookingSource.choices]
    active_customers = bookings.exclude(user__isnull=True).values("user_id").distinct().count()
    previous_customers = previous_bookings.exclude(user__isnull=True).values("user_id").distinct().count()
    return {
        "summary": {"total_revenue": revenue, "total_bookings": booking_count, "average_booking_value": average, "active_customers": active_customers, "revenue_change_percent": change(revenue, previous_revenue), "bookings_change_percent": change(booking_count, previous_bookings.count()), "average_booking_value_change_percent": change(average, previous_average), "active_customers_change_percent": change(active_customers, previous_customers)},
        "revenue_overview": overview,
        "booking_status": {"total": booking_count, "breakdown": breakdown},
        "bookings_by_day": [{"day": day, "label": label, "booking_count": by_day.get(index, 0)} for index, (day, label) in enumerate(weekdays)],
        "revenue_by_source": sources,
        "generated_at": timezone.now(),
    }


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
