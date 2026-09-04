"""Single-venue and whole-hour slot rules."""
import datetime as dt
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from common.utils import local_today
from futsal.models import Futsal, Slot
from futsal.services import generate_slots_for_date, generate_slots_for_range

pytestmark = pytest.mark.django_db

ADMIN_SLOTS = "/api/v1/admin/slots/"


def test_second_futsal_cannot_be_created(futsal):
    with pytest.raises(ValidationError):
        Futsal.objects.create(
            name="Second Futsal", location="Lalitpur", price_per_slot=Decimal("500.00"),
            opening_time=dt.time(6, 0), closing_time=dt.time(22, 0),
        )
    assert Futsal.objects.count() == 1


def test_get_solo_creates_default_when_missing(db):
    assert Futsal.objects.count() == 0
    futsal = Futsal.objects.get_solo()
    assert Futsal.objects.count() == 1
    assert Futsal.objects.get_solo().pk == futsal.pk


def test_public_futsal_endpoint(api, futsal):
    response = api.get("/api/v1/futsal/")
    assert response.status_code == 200
    assert response.data["data"]["name"] == futsal.name


def test_admin_can_update_futsal_config(admin_client, futsal):
    response = admin_client.patch("/api/v1/admin/futsal/",
                                  {"price_per_slot": "1200.00"}, format="json")
    assert response.status_code == 200
    futsal.refresh_from_db()
    assert futsal.price_per_slot == Decimal("1200.00")


def test_slot_created_without_futsal_field(admin_client, futsal):
    response = admin_client.post(ADMIN_SLOTS, {
        "date": (local_today() + dt.timedelta(days=3)).isoformat(),
        "start_time": "07:00", "end_time": "08:00",
    }, format="json")
    assert response.status_code == 201
    assert Slot.objects.get().futsal_id == futsal.id


def test_slot_must_start_on_the_hour(admin_client, futsal):
    response = admin_client.post(ADMIN_SLOTS, {
        "date": (local_today() + dt.timedelta(days=3)).isoformat(),
        "start_time": "07:30", "end_time": "08:30",
    }, format="json")
    assert response.status_code == 400
    assert "start_time" in response.data["errors"]


def test_slot_must_be_exactly_one_hour(admin_client, futsal):
    response = admin_client.post(ADMIN_SLOTS, {
        "date": (local_today() + dt.timedelta(days=3)).isoformat(),
        "start_time": "07:00", "end_time": "09:00",
    }, format="json")
    assert response.status_code == 400
    assert "end_time" in response.data["errors"]


def test_generate_slots_for_date_produces_hourly_slots(futsal):
    created = generate_slots_for_date(date=local_today() + dt.timedelta(days=4))
    assert len(created) == 16  # 06:00 → 22:00
    assert created[0].start_time == dt.time(6, 0)
    assert created[0].end_time == dt.time(7, 0)
    assert created[1].start_time == dt.time(7, 0)
    assert all(
        (dt.datetime.combine(dt.date.min, s.end_time)
         - dt.datetime.combine(dt.date.min, s.start_time)) == dt.timedelta(hours=1)
        for s in created
    )


def test_generate_is_idempotent(futsal):
    date = local_today() + dt.timedelta(days=5)
    first = generate_slots_for_date(date=date)
    second = generate_slots_for_date(date=date)
    assert len(first) == 16 and second == []


def test_admin_generate_endpoint(admin_client, futsal):
    start = local_today() + dt.timedelta(days=6)
    response = admin_client.post(f"{ADMIN_SLOTS}generate/", {
        "start_date": start.isoformat(),
        "end_date": (start + dt.timedelta(days=1)).isoformat(),
    }, format="json")
    assert response.status_code == 201
    assert response.data["data"]["created"] == 32


def test_generate_rejects_past_dates(admin_client, futsal):
    response = admin_client.post(f"{ADMIN_SLOTS}generate/", {
        "start_date": (local_today() - dt.timedelta(days=1)).isoformat(),
    }, format="json")
    assert response.status_code == 400


def test_generate_rejects_reversed_range(admin_client, futsal):
    start = local_today() + dt.timedelta(days=5)
    response = admin_client.post(f"{ADMIN_SLOTS}generate/", {
        "start_date": start.isoformat(),
        "end_date": (start - dt.timedelta(days=2)).isoformat(),
    }, format="json")
    assert response.status_code == 400


def test_generate_requires_admin(user_client, futsal):
    response = user_client.post(f"{ADMIN_SLOTS}generate/",
                                {"start_date": local_today().isoformat()}, format="json")
    assert response.status_code == 403


def test_slot_response_has_no_futsal_field(api, slot):
    row = api.get("/api/v1/slots/").data["data"]["results"][0]
    assert "futsal" not in row
    assert row["start_time"] == "10:00:00"
