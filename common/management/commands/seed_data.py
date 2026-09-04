"""Development seed data. Never use in production."""
from __future__ import annotations

import datetime as dt
import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from bookings.services import create_booking
from common.enums import PaymentMethod, PaymentStatus, UserRole
from common.utils import local_today
from futsal.models import Futsal
from futsal.services import generate_slots_for_range

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "Admin@12345"
USER_PASSWORD = "User@1234"


class Command(BaseCommand):
    help = "Seed development data: admin, users, futsal, slots, bookings and payments."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=7, help="Days of slots to create")

    @transaction.atomic
    def handle(self, *args, **options):
        days: int = options["days"]

        admin, created = User.objects.get_or_create(
            email=ADMIN_EMAIL,
            defaults={"full_name": "Futsal Admin", "phone_number": "9800000001",
                      "role": UserRole.ADMIN, "is_staff": True, "is_superuser": True,
                      "is_verified": True},
        )
        if created:
            admin.set_password(ADMIN_PASSWORD)
            admin.save()

        users = []
        for index in range(1, 4):
            user, was_created = User.objects.get_or_create(
                email=f"user{index}@futsal.local",
                defaults={"full_name": f"Test User {index}",
                          "phone_number": f"98100000{index:02d}",
                          "role": UserRole.USER, "is_verified": True},
            )
            if was_created:
                user.set_password(USER_PASSWORD)
                user.save()
            users.append(user)

        futsal = Futsal.objects.first()
        if futsal is None:
            futsal = Futsal(name="Kathmandu Futsal Arena")
        for field, value in {
            "description": "Premium indoor futsal ground.",
            "location": "Baneshwor",
            "address": "New Baneshwor, Kathmandu",
            "phone": "9800000000",
            "email": "info@futsal.local",
            "price_per_slot": Decimal("1500.00"),
            "slot_duration": 60,
            "opening_time": dt.time(6, 0),
            "closing_time": dt.time(22, 0),
        }.items():
            setattr(futsal, field, value)
        futsal.save()

        today = local_today()
        created_slots = generate_slots_for_range(
            start_date=today, end_date=today + dt.timedelta(days=days - 1)
        )

        bookings = 0
        future_slots = [s for s in created_slots if not s.is_past]
        for slot in random.sample(future_slots, min(6, len(future_slots))):
            user = random.choice(users)
            try:
                create_booking(
                    slot_id=slot.id, full_name=user.full_name, email=user.email,
                    phone_number=user.phone_number, user=user, created_by=user,
                    payment_method=PaymentMethod.CASH, payment_status=PaymentStatus.PAID,
                )
                bookings += 1
            except Exception:  # noqa: BLE001 - slot already booked in a rerun
                continue

        self.stdout.write(self.style.SUCCESS(
            f"Seeded: admin={ADMIN_EMAIL}/{ADMIN_PASSWORD}, users=3 (password {USER_PASSWORD}), "
            f"futsal=1, slots={len(created_slots)}, bookings={bookings}"
        ))
