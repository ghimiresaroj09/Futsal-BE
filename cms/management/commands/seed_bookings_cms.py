"""Management command to seed CMS with bookings page content."""
from django.core.management.base import BaseCommand

from cms import models


class Command(BaseCommand):
    help = "Seeds CMS with bookings page content matching the API contract"

    def handle(self, *args, **options):
        self.stdout.write("Seeding CMS with bookings page content...")
        
        # Bookings Page Meta
        meta = models.BookingsPageMeta.get_solo()
        meta.meta_title = "Book a Slot — Nexus FMS"
        meta.meta_description = (
            "Check live slot availability and book your futsal court online. "
            "Pay at the counter — free rescheduling up to 12 hours before."
        )
        meta.save()
        self.stdout.write(self.style.SUCCESS("✓ Bookings page meta created"))
        
        # Bookings Banner
        banner = models.BookingsBanner.get_solo()
        banner.eyebrow = "Bookings"
        banner.title = "Pick your date. Own your slot."
        banner.description = (
            "Browse the calendar for open hours, choose the slot that fits your squad and "
            "confirm in seconds — pay at the counter, reschedule free up to 12 hours before."
        )
        banner.image_alt = "Nexus Futsal indoor court ready for a match"
        banner.save()
        self.stdout.write(self.style.SUCCESS("✓ Bookings banner created"))
        
        # Bookings Steps Section
        steps_section = models.BookingsStepsSection.get_solo()
        steps_section.heading = "How booking works"
        steps_section.save()
        self.stdout.write(self.style.SUCCESS("✓ Bookings steps section created"))
        
        # Bookings Steps
        steps_data = [
            {
                "key": "date",
                "title": "Pick a date",
                "description": "Browse the calendar — green dots mark dates with open slots.",
                "sort_order": 1,
            },
            {
                "key": "slot",
                "title": "Choose your slot",
                "description": "Select the hour that fits your squad, from morning to prime time.",
                "sort_order": 2,
            },
            {
                "key": "confirm",
                "title": "Confirm & pay at counter",
                "description": "Enter your details to lock the slot, then pay when you arrive.",
                "sort_order": 3,
            },
        ]
        for step in steps_data:
            models.BookingsStep.objects.update_or_create(
                key=step["key"],
                defaults=step
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(steps_data)} booking steps"))
        
        # Bookings Rates Section
        rates_section = models.BookingsRatesSection.get_solo()
        rates_section.heading = "Rates"
        rates_section.description = (
            "Floodlit evenings and weekends cost a little more — that's it. No hidden charges."
        )
        rates_section.weekday_label = "Weekday"
        rates_section.weekend_label = "Weekend"
        rates_section.events_title = "Full arena & events"
        rates_section.events_description = "Tournaments · Corporate · Parties — block bookings welcome"
        rates_section.events_cta_label = "Contact us"
        rates_section.events_cta_href = "/contact"
        rates_section.events_cta_style = "outline"
        rates_section.refreshments_note = "Water, drinks and snacks are sold separately at the counter."
        rates_section.save()
        self.stdout.write(self.style.SUCCESS("✓ Bookings rates section created"))
        
        # Rate Rows
        rate_rows_data = [
            {
                "key": "morning",
                "title": "Morning",
                "hours": "6 AM – 12 PM",
                "weekday_price": 1500,
                "weekend_price": 1800,
                "highlight": False,
                "highlight_label": "",
                "sort_order": 1,
            },
            {
                "key": "afternoon",
                "title": "Afternoon",
                "hours": "12 PM – 5 PM",
                "weekday_price": 2000,
                "weekend_price": 2300,
                "highlight": False,
                "highlight_label": "",
                "sort_order": 2,
            },
            {
                "key": "evening",
                "title": "Evening",
                "hours": "5 PM – 10 PM",
                "weekday_price": 2500,
                "weekend_price": 2800,
                "highlight": True,
                "highlight_label": "Floodlit",
                "sort_order": 3,
            },
        ]
        for row in rate_rows_data:
            models.BookingsRateRow.objects.update_or_create(
                key=row["key"],
                defaults=row
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(rate_rows_data)} rate rows"))
        
        # Bookings Policies Section
        policies_section = models.BookingsPoliciesSection.get_solo()
        policies_section.heading = "Good to know"
        policies_section.save()
        self.stdout.write(self.style.SUCCESS("✓ Bookings policies section created"))
        
        # Policies
        policies_data = [
            {
                "key": "reschedule",
                "icon": "calendar-clock",
                "title": "Free rescheduling",
                "description": "Move or cancel your booking at no cost up to 12 hours before the slot.",
                "sort_order": 1,
            },
            {
                "key": "payment",
                "icon": "wallet",
                "title": "Pay at the counter",
                "description": "No online payment needed — settle up when you arrive at the arena.",
                "sort_order": 2,
            },
            {
                "key": "hold",
                "icon": "shield-check",
                "title": "Slots are held for you",
                "description": "Your booking locks the court for the full hour — nobody else can take it.",
                "sort_order": 3,
            },
            {
                "key": "arrive",
                "icon": "clock",
                "title": "Arrive 10 minutes early",
                "description": "Check in at the counter, grab bibs and a ball, and warm up before kickoff.",
                "sort_order": 4,
            },
        ]
        for policy in policies_data:
            models.BookingsPolicy.objects.update_or_create(
                key=policy["key"],
                defaults=policy
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(policies_data)} policies"))
        
        # Bookings Help Strip
        help_strip = models.BookingsHelpStrip.get_solo()
        help_strip.heading = "Need a hand with your booking?"
        help_strip.description = "Call the arena — we're around from opening to close, every day."
        help_strip.cta_label = "Contact Us"
        help_strip.cta_href = "/contact"
        help_strip.cta_style = "outline"
        help_strip.save()
        self.stdout.write(self.style.SUCCESS("✓ Bookings help strip created"))
        
        self.stdout.write(self.style.SUCCESS("\n✅ Bookings page CMS seeding complete!"))
        self.stdout.write(
            self.style.WARNING(
                "\nNote: Banner image needs to be uploaded via Django admin."
            )
        )
        self.stdout.write("Visit /api/v1/cms/bookings/ to see the result.")
