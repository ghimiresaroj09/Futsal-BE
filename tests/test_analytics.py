"""Aggregate analytics endpoint tests."""
from decimal import Decimal

import pytest

from bookings.services import create_booking
from common.enums import PaymentStatus

pytestmark = pytest.mark.django_db


def test_analytics_returns_documented_dashboard_sections(admin_client, booking):
    response = admin_client.get(
        f"/api/v1/analytics/?start_date={booking.slot.date}&end_date={booking.slot.date}"
    )

    assert response.status_code == 200
    data = response.data["data"]
    assert {"period", "summary", "revenue_overview", "booking_status", "bookings_by_day", "revenue_by_source", "revenue_by_payment_method", "payment_status", "bookings_by_time", "capacity", "booking_performance", "generated_at"} <= set(data)
    assert Decimal(str(data["summary"]["total_revenue"])) == booking.amount
    assert len(data["bookings_by_day"]) == 7
    assert {source["source"] for source in data["revenue_by_source"]} == {"USER", "ADMIN"}
    assert {method["method"] for method in data["revenue_by_payment_method"]} == {
        "CASH", "CARD", "ESEWA", "KHALTI", "BANK_TRANSFER"
    }
    assert {status["status"] for status in data["payment_status"]["breakdown"]} == {
        "PENDING", "ADVANCED", "PAID", "FAILED", "REFUNDED"
    }


def test_analytics_rejects_invalid_period_and_date_range(admin_client):
    assert admin_client.get("/api/v1/analytics/?period=year").status_code == 400
    assert admin_client.get("/api/v1/analytics/?start_date=2026-02-02&end_date=2026-02-01").status_code == 400


def test_analytics_requires_admin(user_client):
    assert user_client.get("/api/v1/analytics/").status_code == 403


def test_analytics_excludes_advanced_payments_from_revenue(admin_client, user, slot):
    create_booking(
        slot_id=slot.id, full_name="Advance User", email="advance@example.com",
        phone_number="9800000093", user=user, advance_amount=Decimal("200.00"),
    )

    response = admin_client.get(
        f"/api/v1/analytics/?start_date={slot.date}&end_date={slot.date}"
    )

    assert response.status_code == 200
    assert Decimal(str(response.data["data"]["summary"]["total_revenue"])) == Decimal("0.00")
