"""MANDATORY: two simultaneous bookings for the same slot must not both succeed."""
from __future__ import annotations

import datetime as dt
import threading
from decimal import Decimal

import pytest
from django.db import connections

from accounts.models import User
from bookings.models import ACTIVE_BOOKING_STATUSES, Booking
from bookings.services import create_booking
from common.exceptions import ConflictError
from common.utils import local_today
from futsal.models import Futsal, Slot


@pytest.mark.django_db(transaction=True)
def test_concurrent_bookings_only_one_succeeds():
    futsal = Futsal.objects.create(
        name="Concurrency Futsal", location="KTM", price_per_slot=Decimal("1000.00"),
        opening_time=dt.time(6, 0), closing_time=dt.time(22, 0),
    )
    slot = Slot.objects.create(
        futsal=futsal, date=local_today() + dt.timedelta(days=1),
        start_time=dt.time(10, 0), end_time=dt.time(11, 0),
    )
    users = [
        User.objects.create_user(email=f"c{i}@example.com", password="Conc@1234",
                                 full_name=f"Conc User {chr(65 + i)}", phone_number=f"981000{i:04d}",
                                 is_verified=True)
        for i in range(2)
    ]

    results: list[str] = []
    barrier = threading.Barrier(2)

    def attempt(user: User) -> None:
        barrier.wait()
        try:
            create_booking(slot_id=slot.id, full_name=user.full_name, email=user.email,
                           phone_number=user.phone_number, user=user)
            results.append("created")
        except Exception as exc:  # noqa: BLE001
            results.append("conflict" if isinstance(exc, ConflictError) else f"error:{exc}")
        finally:
            connections.close_all()

    threads = [threading.Thread(target=attempt, args=(u,)) for u in users]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    assert results.count("created") == 1, results
    assert len(results) == 2
    assert Booking.objects.filter(slot=slot, status__in=ACTIVE_BOOKING_STATUSES).count() == 1


@pytest.mark.django_db
def test_database_constraint_blocks_second_active_booking(user, other_user, slot, booking):
    """Even bypassing the service layer, the DB rejects a second active booking."""
    from django.db import IntegrityError, transaction

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Booking.objects.create(
                booking_reference="FSL-DUPLICATE-0001", user=other_user,
                futsal=slot.futsal, slot=slot, full_name="Other User",
                email="other@example.com", phone_number="9800000012",
                amount=slot.effective_price,
            )


@pytest.mark.django_db
def test_second_request_receives_409(user_client, api, other_user, slot):
    from accounts.services import issue_tokens

    payload = {"slot_id": str(slot.id), "full_name": "John Doe",
               "email": "john@example.com", "phone_number": "9800000000"}
    first = user_client.post("/api/v1/bookings/", payload, format="json")
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {issue_tokens(other_user)['access']}")
    second = api.post("/api/v1/bookings/", payload, format="json")
    assert first.status_code == 201
    assert second.status_code == 409
