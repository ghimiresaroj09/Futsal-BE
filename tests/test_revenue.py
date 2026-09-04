"""Revenue API tests."""
import datetime as dt
from decimal import Decimal

import pytest

from bookings.services import cancel_booking, create_booking
from common.enums import PaymentStatus
from common.utils import local_today
from payments.models import Payment
from tests.conftest import make_slot

pytestmark = pytest.mark.django_db

REVENUE = "/api/v1/admin/revenue/"


def test_revenue_summary(admin_client, booking):
    response = admin_client.get(REVENUE)
    data = response.data["data"]
    assert response.status_code == 200
    assert Decimal(str(data["total_revenue"])) == booking.amount
    assert data["paid_bookings"] == 1
    assert Decimal(str(data["net_revenue"])) == booking.amount


def test_revenue_date_filtering(admin_client, booking):
    date = booking.slot.date
    inside = admin_client.get(
        f"{REVENUE}?start_date={date.isoformat()}&end_date={date.isoformat()}"
    ).data["data"]
    outside_start = (date + dt.timedelta(days=10)).isoformat()
    outside = admin_client.get(
        f"{REVENUE}?start_date={outside_start}&end_date={outside_start}"
    ).data["data"]
    assert inside["number_of_bookings"] == 1
    assert outside["number_of_bookings"] == 0


def test_refunded_booking_reduces_net_revenue(admin_client, booking):
    cancel_booking(booking=booking)
    data = admin_client.get(REVENUE).data["data"]
    assert Decimal(str(data["refunded_amount"])) == booking.amount
    assert Decimal(str(data["net_revenue"])) == Decimal("0.00")
    assert data["cancelled_bookings"] == 1


def test_historical_price_preserved_in_revenue(admin_client, booking, futsal):
    futsal.price_per_slot = Decimal("9999.00")
    futsal.save()
    data = admin_client.get(REVENUE).data["data"]
    assert Decimal(str(data["total_revenue"])) == Decimal("1000.00")


@pytest.mark.parametrize("period", ["daily", "weekly", "monthly"])
def test_period_revenue_endpoints(admin_client, booking, period):
    response = admin_client.get(f"{REVENUE}{period}/")
    assert response.status_code == 200
    assert "summary" in response.data["data"]
    assert isinstance(response.data["data"]["series"], list)


def test_revenue_requires_admin(user_client):
    assert user_client.get(REVENUE).status_code == 403


def test_payment_status_filter(admin_client, booking):
    paid = admin_client.get(f"{REVENUE}?payment_status=PAID").data["data"]
    pending = admin_client.get(f"{REVENUE}?payment_status=PENDING").data["data"]
    assert paid["number_of_bookings"] == 1
    assert pending["number_of_bookings"] == 0
