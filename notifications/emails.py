"""Reusable HTML email service."""
from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger("futsal.email")


def send_html_email(*, subject: str, to: list[str] | str, template: str, context: dict) -> None:
    """Render `emails/<template>.html` and send. Raises on delivery failure."""
    recipients = [to] if isinstance(to, str) else list(to)
    html = render_to_string(f"emails/{template}.html", context)
    message = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    )
    message.attach_alternative(html, "text/html")
    message.send(fail_silently=False)
    logger.info("Email sent: template=%s recipients=%d", template, len(recipients))


def send_otp_email(*, email: str, full_name: str, code: str, purpose: str, expiry_minutes: int) -> None:
    is_reset = purpose == "FORGOT_PASSWORD"
    send_html_email(
        subject="Reset your password" if is_reset else "Verify your email",
        to=email,
        template="otp",
        context={
            "full_name": full_name,
            "code": code,
            "purpose": "Password reset" if is_reset else "Registration",
            "expiry_minutes": expiry_minutes,
        },
    )


def send_booking_confirmation_email(booking) -> None:
    send_html_email(
        subject=f"Booking confirmed - {booking.booking_reference}",
        to=booking.email,
        template="booking_confirmation",
        context={"booking": booking, "slot": booking.slot, "futsal": booking.futsal},
    )


def send_booking_cancellation_email(booking, reason: str = "") -> None:
    send_html_email(
        subject=f"Booking cancelled - {booking.booking_reference}",
        to=booking.email,
        template="booking_cancellation",
        context={"booking": booking, "slot": booking.slot, "reason": reason},
    )


def send_reschedule_email(booking, old_slot) -> None:
    send_html_email(
        subject=f"Booking rescheduled - {booking.booking_reference}",
        to=booking.email,
        template="booking_reschedule",
        context={"booking": booking, "old_slot": old_slot, "new_slot": booking.slot},
    )


def send_booking_reminder_email(booking) -> None:
    send_html_email(
        subject=f"Reminder: your futsal booking {booking.booking_reference} is in 1 hour",
        to=booking.email,
        template="booking_reminder",
        context={"booking": booking, "slot": booking.slot, "futsal": booking.futsal},
    )
