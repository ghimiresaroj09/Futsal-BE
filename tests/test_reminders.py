"""Reminder system tests."""
from __future__ import annotations

import datetime as dt
from unittest import mock

import pytest
from django.core import mail
from django.utils import timezone

from bookings.services import create_booking
from common.enums import PaymentStatus, ReminderStatus, ReminderType
from common.utils import local_now, local_today
from futsal.models import Slot
from notifications.models import Reminder
from notifications.services import (
    send_automatic_reminder, send_manual_reminder, upcoming_bookings_needing_reminder,
)
from notifications.tasks import dispatch_due_reminders

pytestmark = pytest.mark.django_db


@pytest.fixture
def booking_in_one_hour(futsal, user):
    start = local_now() + dt.timedelta(minutes=58)
    slot = Slot.objects.create(
        futsal=futsal, date=start.date(), start_time=start.time().replace(second=0, microsecond=0),
        end_time=(start + dt.timedelta(hours=1)).time().replace(second=0, microsecond=0),
    )
    return create_booking(slot_id=slot.id, full_name="Reminder User",
                          email="reminder@example.com", phone_number="9800000055",
                          user=user, payment_status=PaymentStatus.PAID)


def test_one_hour_calculation_finds_booking(booking_in_one_hour):
    assert booking_in_one_hour in upcoming_bookings_needing_reminder()


def test_far_future_booking_not_selected(booking):
    assert booking not in upcoming_bookings_needing_reminder()


def test_automatic_reminder_sent(booking_in_one_hour):
    mail.outbox.clear()
    reminder = send_automatic_reminder(booking=booking_in_one_hour)
    assert reminder.status == ReminderStatus.SENT
    assert reminder.reminder_type == ReminderType.AUTOMATIC_ONE_HOUR
    assert reminder.sent_at is not None
    assert len(mail.outbox) == 1
    assert "1 hour" in mail.outbox[0].subject


def test_duplicate_automatic_reminder_prevented(booking_in_one_hour):
    send_automatic_reminder(booking=booking_in_one_hour)
    assert send_automatic_reminder(booking=booking_in_one_hour) is None
    assert Reminder.objects.filter(
        booking=booking_in_one_hour, reminder_type=ReminderType.AUTOMATIC_ONE_HOUR
    ).count() == 1


def test_celery_task_dispatches_once(booking_in_one_hour):
    assert dispatch_due_reminders() == 1
    assert dispatch_due_reminders() == 0


def test_failed_email_marks_reminder_failed(booking_in_one_hour):
    with mock.patch("notifications.services.send_booking_reminder_email",
                    side_effect=RuntimeError("SMTP down")):
        reminder = send_automatic_reminder(booking=booking_in_one_hour)
    assert reminder.status == ReminderStatus.FAILED
    assert "SMTP down" in reminder.error_message


def test_manual_reminder_endpoint(admin_client, booking):
    mail.outbox.clear()
    response = admin_client.post(f"/api/v1/admin/bookings/{booking.id}/send-reminder/")
    assert response.status_code == 200
    assert response.data["data"]["reminder_type"] == ReminderType.MANUAL
    assert len(mail.outbox) == 1


def test_manual_reminder_tracked_separately(admin_client, booking_in_one_hour):
    send_automatic_reminder(booking=booking_in_one_hour)
    admin_client.post(f"/api/v1/admin/bookings/{booking_in_one_hour.id}/send-reminder/")
    assert Reminder.objects.filter(booking=booking_in_one_hour).count() == 2
    assert Reminder.objects.filter(reminder_type=ReminderType.MANUAL).count() == 1


def test_admin_can_list_reminders_for_one_booking(admin_client, booking):
    Reminder.objects.create(
        booking=booking, reminder_type=ReminderType.AUTOMATIC_ONE_HOUR,
        scheduled_at=timezone.now(),
    )
    Reminder.objects.create(
        booking=booking, reminder_type=ReminderType.MANUAL,
        scheduled_at=timezone.now(),
    )

    response = admin_client.get(f"/api/v1/admin/bookings/{booking.id}/reminders/")

    assert response.status_code == 200
    data = response.data["data"]
    assert data["count"] == 2
    assert {item["reminder_type"] for item in data["results"]} == {
        ReminderType.AUTOMATIC_ONE_HOUR, ReminderType.MANUAL,
    }


def test_manual_reminder_reports_email_failure(admin_client, booking):
    with mock.patch("notifications.services.send_booking_reminder_email",
                    side_effect=RuntimeError("SMTP down")):
        response = admin_client.post(f"/api/v1/admin/bookings/{booking.id}/send-reminder/")
    assert response.status_code == 502
    assert response.data["success"] is False
    assert Reminder.objects.get().status == ReminderStatus.FAILED


def test_manual_reminder_requires_admin(user_client, booking):
    assert user_client.post(
        f"/api/v1/admin/bookings/{booking.id}/send-reminder/").status_code == 403
