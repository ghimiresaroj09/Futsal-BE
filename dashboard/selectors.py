"""Dashboard aggregations."""
from __future__ import annotations

import datetime as dt
from decimal import Decimal

from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone

from bookings.models import Booking
from common.enums import (
    BookingSource, BookingStatus, PaymentMethod, PaymentStatus, SlotStatus,
)
from futsal.models import FutsalClosure, Slot
from payments.models import Payment

ZERO = Decimal("0.00")


def operational_dashboard(date: dt.date, *, futsal, now: dt.datetime) -> dict:
    """Return the current operating-day dashboard for one facility."""
    slots = Slot.objects.filter(futsal=futsal, date=date).order_by("start_time")
    bookings = (Booking.objects.filter(futsal=futsal, slot__date=date)
                .select_related("slot", "payment"))
    active_bookings = bookings.exclude(status=BookingStatus.CANCELLED)
    paid_payments = Payment.objects.filter(
        booking__futsal=futsal,
        booking__slot__date=date,
        payment_status=PaymentStatus.PAID,
    )
    total_slots = slots.count()
    booked_slots = slots.filter(status=SlotStatus.BOOKED).count()
    upcoming = active_bookings.filter(slot__start_time__gt=now.timetz().replace(tzinfo=None)) if date == now.date() else active_bookings
    next_available = (Slot.objects.filter(futsal=futsal, status=SlotStatus.AVAILABLE)
                      .filter(Q(date__gt=now.date()) | Q(date=now.date(), start_time__gt=now.timetz().replace(tzinfo=None)))
                      .order_by("date", "start_time").first())
    peak = (Booking.objects.filter(futsal=futsal).exclude(status=BookingStatus.CANCELLED)
            .values("slot__start_time", "slot__end_time").annotate(count=Count("id"))
            .order_by("-count", "slot__start_time").first())
    closure = FutsalClosure.objects.filter(futsal=futsal, date__gte=date).order_by("date").first()
    return {
        "date": date,
        "facility": {
            "id": futsal.id,
            "name": futsal.name,
            "opening_time": futsal.opening_time,
            "closing_time": futsal.closing_time,
        },
        "operational_stats": {
            "todays_bookings": bookings.count(),
            "upcoming_bookings": upcoming.count(),
            "available_slots": slots.filter(status=SlotStatus.AVAILABLE).count(),
            "total_slots": total_slots,
            "occupancy_percent": round(booked_slots / total_slots * 100, 1) if total_slots else 0,
            "todays_revenue": paid_payments.aggregate(total=Coalesce(Sum("amount"), ZERO))["total"],
        },
        "slot_availability": [
            {"slot_id": slot.id, "date": slot.date, "start_time": slot.start_time,
             "end_time": slot.end_time, "status": slot.status, "price": slot.effective_price}
            for slot in slots.select_related("futsal")
        ],
        "todays_schedule": [
            {"booking_id": booking.id, "booking_reference": booking.booking_reference,
             "start_time": booking.slot.start_time, "end_time": booking.slot.end_time,
             "full_name": booking.full_name, "futsal_name": futsal.name,
             "status": booking.status,
             "payment_status": getattr(booking.payment, "payment_status", None)}
            for booking in upcoming.order_by("slot__start_time")
        ],
        "facility_snapshot": {
            "next_closed_date": closure.date if closure else None,
            "next_available_slot": ({"date": next_available.date, "start_time": next_available.start_time,
                                     "end_time": next_available.end_time} if next_available else None),
            "peak_booking_window": ({"start_time": peak["slot__start_time"],
                                    "end_time": peak["slot__end_time"]} if peak else None),
            "most_used_slot_duration": futsal.slot_duration,
        },
        "generated_at": timezone.now(),
    }

def analytics(start: dt.date, end: dt.date, *, period: str, futsal_id=None) -> dict:
    """Return the complete analytics dashboard payload for a reporting range."""
    booking_filters = Q(slot__date__gte=start, slot__date__lte=end)
    payment_filters = Q(booking__slot__date__gte=start, booking__slot__date__lte=end, payment_status=PaymentStatus.PAID)
    if futsal_id:
        booking_filters &= Q(futsal_id=futsal_id)
        payment_filters &= Q(booking__futsal_id=futsal_id)
    bookings, payments = Booking.objects.filter(booking_filters), Payment.objects.filter(payment_filters)
    slot_filters = Q(date__gte=start, date__lte=end)
    if futsal_id:
        slot_filters &= Q(futsal_id=futsal_id)
    slots = Slot.objects.filter(slot_filters)
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
    payment_status_rows = {
        row["payment_status"]: row
        for row in Payment.objects.filter(
            Q(booking__slot__date__gte=start, booking__slot__date__lte=end)
            & (Q(booking__futsal_id=futsal_id) if futsal_id else Q())
        ).values("payment_status").annotate(count=Count("id"), amount=Coalesce(Sum("amount"), ZERO))
    }
    payment_status = {
        "total": sum(row["count"] for row in payment_status_rows.values()),
        "breakdown": [
            {"status": status, "label": label,
             "count": payment_status_rows.get(status, {}).get("count", 0),
             "amount": payment_status_rows.get(status, {}).get("amount", ZERO)}
            for status, label in PaymentStatus.choices
        ],
    }
    method_rows = {
        row["payment_method"]: row
        for row in payments.values("payment_method").annotate(
            revenue=Coalesce(Sum("amount"), ZERO), booking_count=Count("id")
        )
    }
    revenue_by_payment_method = [
        {"method": method, "label": label,
         "revenue": method_rows.get(method, {}).get("revenue", ZERO),
         "booking_count": method_rows.get(method, {}).get("booking_count", 0),
         "percentage": round(float(method_rows.get(method, {}).get("revenue", ZERO) / revenue * 100), 1) if revenue else 0}
        for method, label in PaymentMethod.choices
    ]
    time_rows = {
        row["booking__slot__start_time"]: row
        for row in payments.values("booking__slot__start_time", "booking__slot__end_time").annotate(
            revenue=Coalesce(Sum("amount"), ZERO), booking_count=Count("id")
        )
    }
    booking_times = [
        {"start_time": start_time, "end_time": row["booking__slot__end_time"],
         "booking_count": row["booking_count"], "revenue": row["revenue"]}
        for start_time, row in sorted(time_rows.items())
    ]
    slot_counts = dict(slots.values("status").annotate(count=Count("id")).values_list("status", "count"))
    total_slots = slots.count()
    booked_slots = slot_counts.get(SlotStatus.BOOKED, 0)
    cancelled_count = status_counts.get(BookingStatus.CANCELLED, 0)
    completed_count = status_counts.get(BookingStatus.COMPLETED, 0)
    non_cancelled_bookings = booking_count - cancelled_count
    active_customers = bookings.exclude(user__isnull=True).values("user_id").distinct().count()
    previous_customers = previous_bookings.exclude(user__isnull=True).values("user_id").distinct().count()
    return {
        "summary": {"total_revenue": revenue, "total_bookings": booking_count, "average_booking_value": average, "active_customers": active_customers, "revenue_change_percent": change(revenue, previous_revenue), "bookings_change_percent": change(booking_count, previous_bookings.count()), "average_booking_value_change_percent": change(average, previous_average), "active_customers_change_percent": change(active_customers, previous_customers)},
        "revenue_overview": overview,
        "booking_status": {"total": booking_count, "breakdown": breakdown},
        "bookings_by_day": [{"day": day, "label": label, "booking_count": by_day.get(index, 0)} for index, (day, label) in enumerate(weekdays)],
        "revenue_by_source": sources,
        "revenue_by_payment_method": revenue_by_payment_method,
        "payment_status": payment_status,
        "bookings_by_time": booking_times,
        "capacity": {
            "total_slots": total_slots,
            "booked_slots": booked_slots,
            "available_slots": slot_counts.get(SlotStatus.AVAILABLE, 0),
            "blocked_slots": slot_counts.get(SlotStatus.BLOCKED, 0),
            "occupancy_percent": round(booked_slots / total_slots * 100, 1) if total_slots else 0,
        },
        "booking_performance": {
            "cancelled_bookings": cancelled_count,
            "completed_bookings": completed_count,
            "cancellation_rate_percent": round(cancelled_count / booking_count * 100, 1) if booking_count else 0,
            "completion_rate_percent": round(completed_count / non_cancelled_bookings * 100, 1) if non_cancelled_bookings else 0,
        },
        "generated_at": timezone.now(),
    }
