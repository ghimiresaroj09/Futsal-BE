"""Management command to seed CMS with contact page content."""
from django.core.management.base import BaseCommand

from cms import models


class Command(BaseCommand):
    help = "Seeds CMS with contact page content matching the API contract"

    def handle(self, *args, **options):
        self.stdout.write("Seeding CMS with contact page content...")
        
        # Contact Page Meta
        meta = models.ContactPageMeta.get_solo()
        meta.meta_title = "Contact Us — Nexus FMS"
        meta.meta_description = (
            "Questions about bookings, events or coaching? Reach the Nexus Futsal team "
            "by phone, email or the contact form."
        )
        meta.save()
        self.stdout.write(self.style.SUCCESS("✓ Contact page meta created"))
        
        # Contact Header
        header = models.ContactHeader.get_solo()
        header.eyebrow = "Contact Us"
        header.title = "We'd love to hear from you"
        header.description = (
            "Booking questions, event plans, a compliment for the groundskeeper — "
            "drop us a message and we'll get back to you, or reach us directly."
        )
        header.save()
        self.stdout.write(self.style.SUCCESS("✓ Contact header created"))
        
        # Contact Form
        form = models.ContactForm.get_solo()
        form.heading = "Send us a message"
        form.description = "Fill in the form below — we usually reply within a couple of hours."
        form.submit_label = "Send Message"
        form.submitting_label = "Sending…"
        form.success_title = "Message sent!"
        form.success_description = (
            "Thanks {first_name} — we'll reply to {email} within a few hours during opening times."
        )
        form.again_label = "Send another message"
        
        # Field labels and placeholders
        form.name_label = "Full name"
        form.name_placeholder = "Enter your full name"
        form.email_label = "Email"
        form.email_placeholder = "you@example.com"
        form.phone_label = "Phone number"
        form.phone_placeholder = "10-digit mobile number"
        form.subject_label = "Subject"
        form.subject_placeholder = "e.g. Corporate event on a Saturday"
        form.message_label = "Message"
        form.message_placeholder = "Tell us what's on your mind"
        
        form.save()
        self.stdout.write(self.style.SUCCESS("✓ Contact form created"))
        
        # Contact Details Section
        details = models.ContactDetails.get_solo()
        details.heading = "Reach us directly"
        details.description = "The counter is staffed whenever the lights are on."
        details.maps_label = "Get directions"
        details.save()
        self.stdout.write(self.style.SUCCESS("✓ Contact details section created"))
        
        # Contact Detail Items
        detail_items_data = [
            {
                "key": "visit",
                "item_type": "VISIT",
                "label": "Visit",
                "hint": "",
                "value_source": "futsal.address + futsal.location",
                "sort_order": 1,
            },
            {
                "key": "call",
                "item_type": "CALL",
                "label": "Call",
                "hint": "Fastest way to reach us during opening hours.",
                "value_source": "futsal.phone",
                "sort_order": 2,
            },
            {
                "key": "email",
                "item_type": "EMAIL",
                "label": "Email",
                "hint": "We reply within a few hours.",
                "value_source": "futsal.email",
                "sort_order": 3,
            },
            {
                "key": "hours",
                "item_type": "HOURS",
                "label": "Hours",
                "hint": "Open every day of the week.",
                "value_source": "futsal.opening_time + futsal.closing_time",
                "sort_order": 4,
            },
        ]
        for item in detail_items_data:
            models.ContactDetailItem.objects.update_or_create(
                key=item["key"],
                defaults=item
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(detail_items_data)} detail items"))
        
        # Contact Booking Card
        booking_card = models.ContactBookingCard.get_solo()
        booking_card.title = "Looking to book instead?"
        booking_card.description = "Skip the queue — pick your slot online and pay at the counter."
        booking_card.cta_label = "Book a Slot"
        booking_card.cta_href = "/bookings"
        booking_card.cta_style = "primary"
        booking_card.save()
        self.stdout.write(self.style.SUCCESS("✓ Contact booking card created"))
        
        self.stdout.write(self.style.SUCCESS("\n✅ Contact page CMS seeding completed successfully!"))
        self.stdout.write(
            self.style.WARNING(
                "\n⚠️  Note: This provides UI copy only. "
                "Actual contact values come from /api/v1/futsal/ endpoint."
            )
        )
