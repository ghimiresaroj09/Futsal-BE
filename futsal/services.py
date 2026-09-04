"""Slot domain services."""
from __future__ import annotations

import datetime as dt
import logging

from django.db import transaction

from common.enums import SlotStatus
from futsal.models import Futsal, FutsalClosure, Slot

logger = logging.getLogger("futsal.slots")


@transaction.atomic
def generate_slots_for_date(*, date: dt.date, futsal: Futsal | None = None) -> list[Slot]:
    """Generate whole-hour slots between the futsal opening and closing time.

    Slots run on the hour, e.g. 06:00-07:00, 07:00-08:00, ... Existing slots for
    the same start time are left untouched, so this is safe to re-run.
    """
    futsal = futsal or Futsal.objects.get_solo()
    if FutsalClosure.objects.filter(futsal=futsal, date=date).exists():
        logger.info("Skipping slot generation for closed date=%s", date)
        return []
    created: list[Slot] = []
    duration = dt.timedelta(hours=1)
    cursor = dt.datetime.combine(date, futsal.opening_time)
    closing = dt.datetime.combine(date, futsal.closing_time)
    while cursor + duration <= closing:
        end = cursor + duration
        slot, was_created = Slot.objects.get_or_create(
            futsal=futsal,
            date=date,
            start_time=cursor.time(),
            defaults={"end_time": end.time(), "status": SlotStatus.AVAILABLE},
        )
        if was_created:
            created.append(slot)
        cursor = end
    logger.info("Generated %d slots for date=%s", len(created), date)
    return created


@transaction.atomic
def generate_slots_for_range(*, start_date: dt.date, end_date: dt.date) -> list[Slot]:
    """Generate whole-hour slots for every date in an inclusive range."""
    futsal = Futsal.objects.get_solo()
    created: list[Slot] = []
    current = start_date
    while current <= end_date:
        created += generate_slots_for_date(date=current, futsal=futsal)
        current += dt.timedelta(days=1)
    return created


@transaction.atomic
def copy_slots_to_next_day(*, date: dt.date, futsal: Futsal | None = None) -> list[Slot]:
    """Copy a day's slot layout to the following date without bookings or status."""
    futsal = futsal or Futsal.objects.get_solo()
    source_date = date - dt.timedelta(days=1)
    source_slots = Slot.objects.filter(futsal=futsal, date=source_date).order_by("start_time")
    created: list[Slot] = []
    for source in source_slots:
        slot, was_created = Slot.objects.get_or_create(
            futsal=futsal,
            date=date,
            start_time=source.start_time,
            defaults={
                "end_time": source.end_time,
                "price": source.price,
                "status": SlotStatus.AVAILABLE,
            },
        )
        if was_created:
            created.append(slot)
    logger.info(
        "Copied %d slot(s) from date=%s to date=%s", len(created), source_date, date
    )
    return created


@transaction.atomic
def bulk_update_slots_for_date(*, date: dt.date, updates: dict,
                               futsal: Futsal | None = None) -> dict:
    """Update selected fields for every slot on a date, excluding booked statuses."""
    from bookings.models import ACTIVE_BOOKING_STATUSES, Booking

    futsal = futsal or Futsal.objects.get_solo()
    slots = list(Slot.objects.select_for_update().filter(futsal=futsal, date=date))
    booked_slot_ids = set(
        Booking.objects.filter(slot_id__in=[slot.id for slot in slots],
                                status__in=ACTIVE_BOOKING_STATUSES)
        .values_list("slot_id", flat=True)
    )
    updated = 0
    skipped_booked = 0
    updated_slots = []
    for slot in slots:
        if "status" in updates and slot.id in booked_slot_ids:
            skipped_booked += 1
            if len(updates) == 1:
                continue
        for field, value in updates.items():
            if field == "status" and slot.id in booked_slot_ids:
                continue
            setattr(slot, field, value)
        slot.save(update_fields=[*updates.keys(), "updated_at"])
        updated += 1
        updated_slots.append(slot)
    logger.info("Bulk-updated slots date=%s updated=%d skipped_booked=%d",
                date, updated, skipped_booked)
    return {
        "date": date,
        "updated_slots": updated,
        "skipped_booked_slots": skipped_booked,
        "slots": updated_slots,
    }


@transaction.atomic
def bulk_update_named_slots(*, date: dt.date, slot_updates: list[dict],
                            futsal: Futsal | None = None) -> dict:
    """Apply different updates to selected slots on one date."""
    from bookings.models import ACTIVE_BOOKING_STATUSES, Booking

    futsal = futsal or Futsal.objects.get_solo()
    slots = {
        (slot.start_time, slot.end_time): slot
        for slot in Slot.objects.select_for_update().filter(futsal=futsal, date=date)
    }
    requested_pairs = [(item["start_time"], item["end_time"]) for item in slot_updates]
    booked_slot_ids = set(
        Booking.objects.filter(
            slot__futsal=futsal, slot__date=date,
            slot__start_time__in=[start for start, _ in requested_pairs],
            status__in=ACTIVE_BOOKING_STATUSES,
        ).values_list("slot_id", flat=True)
    )
    updated = 0
    skipped_booked = 0
    not_found = []
    updated_slots = []
    for item in slot_updates:
        slot = slots.get((item["start_time"], item["end_time"]))
        if slot is None:
            not_found.append(
                f"{item['start_time']:%H:%M}-{item['end_time']:%H:%M}"
            )
            continue
        if "status" in item and slot.id in booked_slot_ids:
            skipped_booked += 1
        for field, value in item.items():
            if field == "status" and slot.id in booked_slot_ids:
                continue
            setattr(slot, field, value)
        slot.save(update_fields=[*item.keys(), "updated_at"])
        updated += 1
        updated_slots.append(slot)
    return {
        "date": date,
        "updated_slots": updated,
        "skipped_booked_slots": skipped_booked,
        "not_found_start_times": not_found,
        "slots": updated_slots,
    }


# --------------------------------------------------------------- day blocking
@transaction.atomic
def block_day(*, date: dt.date, reason: str = "", actor=None,
              cancel_bookings: bool = False) -> dict:
    """Close the futsal for an entire day.

    All AVAILABLE slots on the date become BLOCKED. Slots that already carry an
    active booking are reported back and left untouched, unless
    ``cancel_bookings=True``, in which case those bookings are cancelled (which
    refunds the payment and notifies the customer) and the slots are blocked too.
    """
    from bookings.models import ACTIVE_BOOKING_STATUSES, Booking
    from bookings.services import cancel_booking
    from common.enums import BookingStatus

    futsal = Futsal.objects.get_solo()
    closure, _ = FutsalClosure.objects.update_or_create(
        futsal=futsal, date=date,
        defaults={"reason": reason, "created_by": actor},
    )

    slots = Slot.objects.select_for_update().filter(futsal=futsal, date=date)
    booked_ids = list(
        Booking.objects.filter(slot__in=slots, status__in=ACTIVE_BOOKING_STATUSES)
        .values_list("id", flat=True)
    )

    cancelled = 0
    if cancel_bookings and booked_ids:
        for booking in Booking.objects.filter(id__in=booked_ids).select_related("slot"):
            cancel_booking(booking=booking, actor=actor,
                           reason=reason or "Futsal closed for the day")
            cancelled += 1
        booked_ids = []

    blocked = Slot.objects.filter(
        futsal=futsal, date=date, status=SlotStatus.AVAILABLE
    ).update(status=SlotStatus.BLOCKED)

    logger.info("Day blocked date=%s blocked=%d cancelled=%d actor=%s",
                date, blocked, cancelled, getattr(actor, "id", None))
    return {
        "date": date,
        "reason": closure.reason,
        "blocked_slots": blocked,
        "cancelled_bookings": cancelled,
        "skipped_booked_slots": len(booked_ids),
    }


@transaction.atomic
def unblock_day(*, date: dt.date, actor=None) -> dict:
    """Reopen a closed day: BLOCKED slots return to AVAILABLE."""
    futsal = Futsal.objects.get_solo()
    FutsalClosure.objects.filter(futsal=futsal, date=date).delete()
    released = Slot.objects.filter(
        futsal=futsal, date=date, status=SlotStatus.BLOCKED
    ).update(status=SlotStatus.AVAILABLE)
    logger.info("Day unblocked date=%s released=%d actor=%s",
                date, released, getattr(actor, "id", None))
    return {"date": date, "released_slots": released}
