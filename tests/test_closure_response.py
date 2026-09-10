"""Tests for closure response in public slot endpoints."""
import datetime as dt

import pytest
from common.utils import local_today
from futsal.models import Futsal, FutsalClosure, Slot

PUBLIC_SLOTS = "/api/v1/slots/"


@pytest.fixture
def futsal():
    return Futsal.objects.get_solo()


@pytest.mark.django_db
def test_date_wise_shows_closure_message(api, futsal):
    """date-wise endpoint should return closure info when date is blocked."""
    target_date = local_today() + dt.timedelta(days=3)
    
    # Create some slots
    Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(10, 0),
        end_time=dt.time(11, 0)
    )
    Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(11, 0),
        end_time=dt.time(12, 0)
    )
    
    # Block the day
    FutsalClosure.objects.create(
        futsal=futsal,
        date=target_date,
        reason="Public Holiday - Dashain"
    )
    
    # Request slots for that date
    response = api.get(f"{PUBLIC_SLOTS}date-wise/?date={target_date.isoformat()}")
    
    assert response.status_code == 200
    data = response.data["data"]
    
    # Should return closure info
    assert data["is_closed"] is True
    assert data["reason"] == "Public Holiday - Dashain"
    assert data["date"] == str(target_date)
    assert data["slots"] == []
    
    # Message should mention closure
    assert "closed" in response.data["message"].lower()
    assert "Dashain" in response.data["message"]


@pytest.mark.django_db
def test_list_with_date_filter_shows_closure(api, futsal):
    """list endpoint with date filter should return closure info."""
    target_date = local_today() + dt.timedelta(days=5)
    
    # Create slots
    Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(14, 0),
        end_time=dt.time(15, 0)
    )
    
    # Block the day
    FutsalClosure.objects.create(
        futsal=futsal,
        date=target_date,
        reason="Maintenance Work"
    )
    
    # Request with date filter
    response = api.get(f"{PUBLIC_SLOTS}?date={target_date.isoformat()}")
    
    assert response.status_code == 200
    data = response.data["data"]
    
    # Should return closure info
    assert data["is_closed"] is True
    assert data["reason"] == "Maintenance Work"
    assert data["results"] == []


@pytest.mark.django_db
def test_closure_without_reason_shows_default_message(api, futsal):
    """Closure without reason should show default message."""
    target_date = local_today() + dt.timedelta(days=7)
    
    # Block day without reason
    FutsalClosure.objects.create(
        futsal=futsal,
        date=target_date,
        reason=""  # No reason provided
    )
    
    response = api.get(f"{PUBLIC_SLOTS}date-wise/?date={target_date.isoformat()}")
    
    assert response.status_code == 200
    data = response.data["data"]
    
    assert data["is_closed"] is True
    assert data["reason"] == "Facility closed"
    assert "No bookings available" in response.data["message"]


@pytest.mark.django_db
def test_open_date_returns_normal_slots(api, futsal):
    """Open date should return normal slot list."""
    target_date = local_today() + dt.timedelta(days=10)
    
    # Create slots (no closure)
    Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(10, 0),
        end_time=dt.time(11, 0)
    )
    Slot.objects.create(
        futsal=futsal,
        date=target_date,
        start_time=dt.time(11, 0),
        end_time=dt.time(12, 0)
    )
    
    response = api.get(f"{PUBLIC_SLOTS}date-wise/?date={target_date.isoformat()}")
    
    assert response.status_code == 200
    data = response.data["data"]
    
    # Should NOT have closure info
    assert "is_closed" not in data or data.get("is_closed") is False
    
    # Should have results
    results = data.get("results", [])
    assert len(results) == 2


@pytest.mark.django_db
def test_list_without_date_filter_ignores_closures(api, futsal):
    """List without date filter should show all upcoming slots normally."""
    today = local_today()
    
    # Create slots for multiple days
    Slot.objects.create(
        futsal=futsal,
        date=today + dt.timedelta(days=1),
        start_time=dt.time(10, 0),
        end_time=dt.time(11, 0)
    )
    Slot.objects.create(
        futsal=futsal,
        date=today + dt.timedelta(days=2),
        start_time=dt.time(10, 0),
        end_time=dt.time(11, 0)
    )
    
    # Block one day
    FutsalClosure.objects.create(
        futsal=futsal,
        date=today + dt.timedelta(days=2),
        reason="Closed"
    )
    
    # List all (no date filter)
    response = api.get(PUBLIC_SLOTS)
    
    assert response.status_code == 200
    
    # Should return normal paginated list (not closure info)
    assert "results" in response.data["data"]
    assert "is_closed" not in response.data["data"]
