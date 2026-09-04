"""Slot management tests."""
import datetime as dt

import pytest

from common.enums import SlotStatus
from common.utils import local_today
from futsal.models import Slot

pytestmark = pytest.mark.django_db

ADMIN_SLOTS = "/api/v1/admin/slots/"
PUBLIC_SLOTS = "/api/v1/slots/"


def payload(futsal, hour=15, days=2):
    return {
        "date": (local_today() + dt.timedelta(days=days)).isoformat(),
        "start_time": f"{hour:02d}:00",
        "end_time": f"{hour + 1:02d}:00",
    }


def test_admin_can_create_slot(admin_client, futsal):
    response = admin_client.post(ADMIN_SLOTS, payload(futsal), format="json")
    assert response.status_code == 201
    assert response.data["data"]["status"] == SlotStatus.AVAILABLE


def test_admin_can_copy_previous_day_slots(admin_client, futsal):
    source_date = local_today() - dt.timedelta(days=1)
    target_date = local_today()
    source = Slot.objects.create(
        futsal=futsal, date=source_date, start_time=dt.time(10, 0),
        end_time=dt.time(11, 0), price=750, status=SlotStatus.BLOCKED,
    )

    response = admin_client.post(
        f"{ADMIN_SLOTS}copy-next-day/", {"date": target_date.isoformat()}, format="json"
    )

    assert response.status_code == 201
    copied = Slot.objects.get(futsal=futsal, date=target_date, start_time=source.start_time)
    assert copied.end_time == source.end_time
    assert copied.price == source.price
    assert copied.status == SlotStatus.AVAILABLE

    second = admin_client.post(
        f"{ADMIN_SLOTS}copy-next-day/", {"date": target_date.isoformat()}, format="json"
    )
    assert second.status_code == 200
    assert second.data["data"]["created"] == 0


def test_admin_can_bulk_update_slots_by_date(admin_client, futsal):
    target_date = local_today() + dt.timedelta(days=2)
    Slot.objects.create(futsal=futsal, date=target_date, start_time=dt.time(10, 0),
                        end_time=dt.time(11, 0))
    Slot.objects.create(futsal=futsal, date=target_date, start_time=dt.time(11, 0),
                        end_time=dt.time(12, 0))

    response = admin_client.patch(
        f"{ADMIN_SLOTS}bulk-update/",
        {"date": target_date.isoformat(), "status": SlotStatus.BLOCKED, "price": "900.00"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["data"]["updated_slots"] == 2
    assert len(response.data["data"]["slots"]) == 2
    assert Slot.objects.filter(date=target_date, status=SlotStatus.BLOCKED,
                               price=900).count() == 2


def test_admin_can_bulk_update_different_slot_prices(admin_client, futsal):
    target_date = local_today() + dt.timedelta(days=3)
    Slot.objects.create(futsal=futsal, date=target_date, start_time=dt.time(10, 0),
                        end_time=dt.time(11, 0))
    Slot.objects.create(futsal=futsal, date=target_date, start_time=dt.time(20, 0),
                        end_time=dt.time(21, 0))

    response = admin_client.patch(
        f"{ADMIN_SLOTS}bulk-update/",
        {"date": target_date.isoformat(), "slots": [
            {"start_time": "10:00", "end_time": "11:00", "price": "1000.00"},
            {"start_time": "20:00", "end_time": "21:00", "price": "1500.00"},
        ]},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["data"]["updated_slots"] == 2
    assert {slot["price"] for slot in response.data["data"]["slots"]} == {"1000.00", "1500.00"}
    assert Slot.objects.get(date=target_date, start_time=dt.time(10, 0)).price == 1000
    assert Slot.objects.get(date=target_date, start_time=dt.time(20, 0)).price == 1500


def test_bulk_update_requires_an_update_field(admin_client):
    response = admin_client.patch(
        f"{ADMIN_SLOTS}bulk-update/", {"date": local_today().isoformat()}, format="json"
    )
    assert response.status_code == 400


def test_slot_start_must_be_before_end(admin_client, futsal):
    data = payload(futsal)
    data["end_time"] = data["start_time"]
    assert admin_client.post(ADMIN_SLOTS, data, format="json").status_code == 400


def test_slot_cannot_be_created_in_the_past(admin_client, futsal):
    data = payload(futsal)
    data["date"] = (local_today() - dt.timedelta(days=1)).isoformat()
    assert admin_client.post(ADMIN_SLOTS, data, format="json").status_code == 400


def test_overlapping_slot_rejected(admin_client, futsal, slot):
    data = {"date": slot.date.isoformat(), "start_time": "10:00", "end_time": "11:00"}
    assert admin_client.post(ADMIN_SLOTS, data, format="json").status_code == 400


def test_admin_can_update_slot(admin_client, slot):
    response = admin_client.patch(f"{ADMIN_SLOTS}{slot.id}/", {"status": SlotStatus.BLOCKED},
                                  format="json")
    assert response.status_code == 200
    slot.refresh_from_db()
    assert slot.status == SlotStatus.BLOCKED


def test_admin_can_delete_slot(admin_client, slot):
    response = admin_client.delete(f"{ADMIN_SLOTS}{slot.id}/")
    assert response.status_code == 200
    assert response.data == {
        "success": True,
        "message": "Slot deleted successfully",
    }
    assert not Slot.objects.filter(pk=slot.pk).exists()


def test_booked_slot_cannot_be_deleted(admin_client, booking):
    response = admin_client.delete(f"{ADMIN_SLOTS}{booking.slot_id}/")
    assert response.status_code == 409


def test_slot_date_filtering(admin_client, slot, futsal):
    other = Slot.objects.create(futsal=futsal, date=slot.date + dt.timedelta(days=1),
                                start_time=dt.time(9, 0), end_time=dt.time(10, 0))
    response = admin_client.get(f"{ADMIN_SLOTS}?date={slot.date.isoformat()}")
    ids = [row["id"] for row in response.data["data"]["results"]]
    assert str(slot.id) in ids and str(other.id) not in ids


def test_slot_status_filtering(admin_client, futsal, slot):
    Slot.objects.create(futsal=futsal, date=slot.date, start_time=dt.time(20, 0),
                        end_time=dt.time(21, 0), status=SlotStatus.BLOCKED)
    response = admin_client.get(f"{ADMIN_SLOTS}?status=BLOCKED")
    assert response.data["data"]["count"] == 1


def test_public_slot_listing_excludes_past_slots(api, slot, past_slot):
    response = api.get(PUBLIC_SLOTS)
    ids = [row["id"] for row in response.data["data"]["results"]]
    assert str(slot.id) in ids
    assert str(past_slot.id) not in ids


def test_public_slot_date_filter(api, slot):
    response = api.get(f"{PUBLIC_SLOTS}?date={slot.date.isoformat()}")
    assert response.status_code == 200
    assert response.data["data"]["count"] == 1


def test_public_date_wise_slots(api, futsal):
    target_date = local_today() + dt.timedelta(days=2)
    Slot.objects.create(futsal=futsal, date=target_date, start_time=dt.time(10, 0),
                        end_time=dt.time(11, 0))

    response = api.get(f"{PUBLIC_SLOTS}date-wise/?date={target_date.isoformat()}")

    assert response.status_code == 200
    assert response.data["data"]["count"] == 1
    assert response.data["data"]["results"][0]["date"] == target_date.isoformat()


def test_public_date_wise_requires_date(api):
    response = api.get(f"{PUBLIC_SLOTS}date-wise/")
    assert response.status_code == 400


def test_pagination_metadata(api, slot):
    response = api.get(f"{PUBLIC_SLOTS}?page=1&page_size=1")
    data = response.data["data"]
    assert {"count", "next", "previous", "results"} <= set(data)
