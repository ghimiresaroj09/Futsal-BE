"""Shared pytest fixtures."""
from __future__ import annotations

import datetime as dt
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from accounts.models import User
from common.enums import PaymentStatus, UserRole
from common.utils import local_now, local_today
from futsal.models import Futsal, Slot


@pytest.fixture
def api() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(
        email="user@example.com", password="User@1234", full_name="Normal User",
        phone_number="9800000011", is_verified=True,
    )


@pytest.fixture
def other_user(db) -> User:
    return User.objects.create_user(
        email="other@example.com", password="Other@1234", full_name="Other User",
        phone_number="9800000012", is_verified=True,
    )


@pytest.fixture
def admin_user(db) -> User:
    return User.objects.create_user(
        email="admin@example.com", password="Admin@1234", full_name="Admin User",
        phone_number="9800000013", role=UserRole.ADMIN, is_verified=True, is_staff=True,
    )


def _auth(api: APIClient, user: User) -> APIClient:
    from accounts.services import issue_tokens

    api.credentials(HTTP_AUTHORIZATION=f"Bearer {issue_tokens(user)['access']}")
    return api


@pytest.fixture
def user_client(api, user) -> APIClient:
    return _auth(api, user)


@pytest.fixture
def admin_client(admin_user) -> APIClient:
    return _auth(APIClient(), admin_user)


@pytest.fixture
def futsal(db) -> Futsal:
    """The single futsal venue."""
    return Futsal.objects.create(
        name="Test Futsal", location="Kathmandu", address="Baneshwor",
        phone="9800000000", email="f@example.com", price_per_slot=Decimal("1000.00"),
        slot_duration=60, opening_time=dt.time(6, 0), closing_time=dt.time(22, 0),
    )


def make_slot(futsal, *, days_ahead: int = 1, hour: int = 10, **kwargs) -> Slot:
    date = local_today() + dt.timedelta(days=days_ahead)
    return Slot.objects.create(
        futsal=futsal, date=date, start_time=dt.time(hour, 0),
        end_time=dt.time(hour + 1, 0), **kwargs
    )


@pytest.fixture
def slot(futsal) -> Slot:
    return make_slot(futsal)


@pytest.fixture
def second_slot(futsal) -> Slot:
    return make_slot(futsal, hour=12)


@pytest.fixture
def past_slot(futsal) -> Slot:
    yesterday = local_today() - dt.timedelta(days=1)
    return Slot.objects.create(futsal=futsal, date=yesterday,
                               start_time=dt.time(10, 0), end_time=dt.time(11, 0))


@pytest.fixture
def booking(user, slot):
    from bookings.services import create_booking

    return create_booking(
        slot_id=slot.id, full_name="Normal User", email="user@example.com",
        phone_number="9800000011", user=user, created_by=user,
        payment_status=PaymentStatus.PAID,
    )
