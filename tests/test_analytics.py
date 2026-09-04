"""Aggregate analytics endpoint tests."""
from decimal import Decimal

import pytest

pytestmark = pytest.mark.django_db


def test_analytics_returns_documented_dashboard_sections(admin_client, booking):
    response = admin_client.get(
        f"/api/v1/analytics/?start_date={booking.slot.date}&end_date={booking.slot.date}"
    )

    assert response.status_code == 200
    data = response.data["data"]
    assert {"period", "summary", "revenue_overview", "booking_status", "bookings_by_day", "revenue_by_source", "generated_at"} <= set(data)
    assert Decimal(str(data["summary"]["total_revenue"])) == booking.amount
    assert len(data["bookings_by_day"]) == 7
    assert {source["source"] for source in data["revenue_by_source"]} == {"USER", "ADMIN"}


def test_analytics_rejects_invalid_period_and_date_range(admin_client):
    assert admin_client.get("/api/v1/analytics/?period=year").status_code == 400
    assert admin_client.get("/api/v1/analytics/?start_date=2026-02-02&end_date=2026-02-01").status_code == 400


def test_analytics_requires_admin(user_client):
    assert user_client.get("/api/v1/analytics/").status_code == 403
