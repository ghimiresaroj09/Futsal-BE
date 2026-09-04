"""Admin in-app booking notification API tests."""
from __future__ import annotations

import pytest

from bookings.services import cancel_booking, create_booking
from common.enums import PaymentStatus
from notifications.models import AdminNotification
from notifications.services import booking_slot_description


pytestmark = pytest.mark.django_db


def _create_booking(slot, user):
    return create_booking(
        slot_id=slot.id,
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
        user=user,
        created_by=user,
        payment_status=PaymentStatus.PAID,
    )


def test_customer_booking_creates_admin_notification(admin_user, user, slot):
    booking = _create_booking(slot, user)

    notification = AdminNotification.objects.get(recipient=admin_user)
    assert notification.booking == booking
    assert notification.is_read is False
    assert notification.message == (
        f"Normal User booked a slot for {booking_slot_description(booking)}."
    )


def test_admin_notification_list_filters_and_links_to_booking(admin_client, admin_user, user, slot):
    booking = _create_booking(slot, user)
    notification = AdminNotification.objects.get(recipient=admin_user)
    notification.is_read = True
    notification.save(update_fields=["is_read", "updated_at"])

    response = admin_client.get("/api/v1/admin/notifications/?read=read")

    assert response.status_code == 200
    result = response.data["data"]["results"]
    assert len(result) == 1
    assert result[0]["booking"] == booking.id
    assert result[0]["redirect_url"] == f"/admin/bookings/{booking.id}"
    assert result[0]["time_ago"]
    assert response.data["data"]["unread_count"] == 0
    assert admin_client.get("/api/v1/admin/notifications/?read=unread").data["data"]["count"] == 0


def test_notifications_are_newest_first_and_paginated(admin_client, admin_user, user, slot, second_slot):
    first = _create_booking(slot, user)
    second = _create_booking(second_slot, user)

    response = admin_client.get("/api/v1/admin/notifications/?page_size=1&ordering=created_at")

    assert response.status_code == 200
    data = response.data["data"]
    assert data["count"] == 2
    assert len(data["results"]) == 1
    assert data["results"][0]["booking"] == second.id


def test_mark_single_and_all_notifications_as_read(admin_client, admin_user, user, slot, second_slot):
    first = _create_booking(slot, user)
    second = _create_booking(second_slot, user)
    first_notification = AdminNotification.objects.get(recipient=admin_user, booking=first)

    response = admin_client.post(f"/api/v1/admin/notifications/{first_notification.id}/mark-read/")
    assert response.status_code == 200
    assert response.data["data"]["is_read"] is True
    assert response.data["data"]["read_at"] is not None

    response = admin_client.post("/api/v1/admin/notifications/mark-all-read/")
    assert response.status_code == 200
    assert response.data["data"]["marked_as_read"] == 1
    assert response.data["data"]["unread_count"] == 0
    assert not AdminNotification.objects.filter(recipient=admin_user, is_read=False).exists()

    response = admin_client.post(f"/api/v1/admin/notifications/{first_notification.id}/mark-unread/")
    assert response.status_code == 200
    assert response.data["data"]["is_read"] is False


def test_customer_cancellation_creates_admin_notification(admin_user, user, slot):
    booking = _create_booking(slot, user)

    cancel_booking(booking=booking, actor=user, reason="Plans changed")

    notifications = AdminNotification.objects.filter(recipient=admin_user).order_by("created_at")
    assert notifications.count() == 2
    assert notifications.last().title == "Booking cancelled"
    assert notifications.last().message == (
        f"Normal User cancelled their booking for {booking_slot_description(booking)}."
    )


def test_admin_cancellation_creates_notification(admin_user, user, admin_client, slot):
    booking = _create_booking(slot, user)

    response = admin_client.post(f"/api/v1/admin/bookings/{booking.id}/cancel/")

    assert response.status_code == 200
    assert AdminNotification.objects.filter(recipient=admin_user).count() == 2


def test_admin_cannot_access_another_admin_notification(admin_client, admin_user, user, slot, other_user):
    booking = _create_booking(slot, user)
    notification = AdminNotification.objects.get(recipient=admin_user, booking=booking)
    other_user.role = "ADMIN"
    other_user.is_staff = True
    other_user.save(update_fields=["role", "is_staff", "updated_at"])

    from accounts.services import issue_tokens
    from rest_framework.test import APIClient

    other_client = APIClient()
    other_client.credentials(HTTP_AUTHORIZATION=f"Bearer {issue_tokens(other_user)['access']}")
    assert other_client.get(f"/api/v1/admin/notifications/{notification.id}/").status_code == 404
