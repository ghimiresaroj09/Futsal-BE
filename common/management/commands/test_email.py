"""Send a test email to verify SMTP configuration.

Usage::

    python manage.py test_email                 # sends to EMAIL_HOST_USER
    python manage.py test_email you@example.com
"""
from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from notifications.emails import send_html_email


class Command(BaseCommand):
    help = "Send a test email to verify the SMTP configuration."

    def add_arguments(self, parser):
        parser.add_argument("recipient", nargs="?", default=None,
                            help="Recipient address (defaults to EMAIL_HOST_USER).")

    def handle(self, *args, **options):
        recipient = options["recipient"] or settings.EMAIL_HOST_USER
        if not recipient:
            raise CommandError("No recipient given and EMAIL_HOST_USER is empty.")

        self.stdout.write(
            f"Backend: {settings.EMAIL_BACKEND}\n"
            f"Host   : {settings.EMAIL_HOST}:{settings.EMAIL_PORT} (TLS={settings.EMAIL_USE_TLS})\n"
            f"From   : {settings.DEFAULT_FROM_EMAIL}\n"
            f"To     : {recipient}"
        )
        try:
            send_html_email(
                subject="Futsal API - SMTP test",
                to=recipient,
                template="otp",
                context={"full_name": "Administrator", "code": "123456",
                         "purpose": "SMTP test", "expiry_minutes": 10},
            )
        except Exception as exc:  # noqa: BLE001 - surface the real reason to the operator
            raise CommandError(f"Email delivery failed: {type(exc).__name__}: {exc}")
        self.stdout.write(self.style.SUCCESS("Test email sent successfully."))
