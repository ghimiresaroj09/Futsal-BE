"""Management command to seed CMS with initial homepage content."""
from django.core.management.base import BaseCommand

from cms import models


class Command(BaseCommand):
    help = "Seeds CMS with initial homepage content matching the API contract"

    def handle(self, *args, **options):
        self.stdout.write("Seeding CMS with homepage content...")
        
        # Homepage Meta
        meta = models.HomepageMeta.get_solo()
        meta.meta_title = "Nexus FMS — Book Your Futsal Slot Online"
        meta.meta_description = (
            "Premium futsal courts in Kathmandu. Check live availability and book your slot "
            "online in seconds — pay at the counter."
        )
        meta.save()
        self.stdout.write(self.style.SUCCESS("✓ Homepage meta created"))
        
        # Hero Section
        hero = models.HeroSection.get_solo()
        hero.badge = "Kathmandu's home of futsal"
        hero.title = "Book your slot."
        hero.title_highlight = "Own the game."
        hero.description = (
            "Premium turf, floodlights and locker rooms at Nexus Futsal — reserve your hour "
            "online in seconds, gather your squad and just show up to play."
        )
        hero.image_alt = "Players in a mid-match action on the Nexus Futsal court"
        hero.primary_cta_label = "Book a Slot"
        hero.primary_cta_href = "/bookings"
        hero.primary_cta_style = "primary"
        hero.secondary_cta_label = "Explore Gallery"
        hero.secondary_cta_href = "/gallery"
        hero.secondary_cta_style = "outline"
        hero.save()
        self.stdout.write(self.style.SUCCESS("✓ Hero section created"))
        
        # Stats
        stats_data = [
            {"key": "courts", "value": "2", "label": "Premium courts", "sort_order": 1},
            {"key": "matches", "value": "20K+", "label": "Matches hosted", "sort_order": 2},
            {"key": "hours", "value": "6AM–10PM", "label": "Open every day", "sort_order": 3},
        ]
        for stat in stats_data:
            models.StatItem.objects.update_or_create(
                key=stat["key"],
                defaults=stat
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(stats_data)} stat items"))
        
        # Arena Section
        arena = models.ArenaSection.get_solo()
        arena.eyebrow = "The Arena"
        arena.heading = "One arena. Built for the game."
        arena.description = (
            "Run by players, for players. Two meticulously maintained courts, quality gear and "
            "a space that's always match-ready — whether it's a casual kickabout or a cup final."
        )
        arena.since_label = "Since 2018"
        arena.save()
        self.stdout.write(self.style.SUCCESS("✓ Arena section created"))
        
        # Arena Highlights
        highlights_data = [
            {"key": "turf", "icon": "sparkles", "text": "FIFA-quality imported turf", "sort_order": 1},
            {"key": "lights", "icon": "zap", "text": "Floodlights every evening", "sort_order": 2},
            {"key": "rooms", "icon": "shield-check", "text": "Changing rooms & hot showers", "sort_order": 3},
            {"key": "wifi", "icon": "wifi", "text": "Free Wi-Fi & spectator lounge", "sort_order": 4},
            {"key": "gear", "icon": "dumbbell", "text": "Bibs, balls & equipment provided", "sort_order": 5},
            {"key": "parking", "icon": "map-pin", "text": "Ample free parking", "sort_order": 6},
        ]
        for highlight in highlights_data:
            models.ArenaHighlight.objects.update_or_create(
                key=highlight["key"],
                defaults=highlight
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(highlights_data)} arena highlights"))
        
        # Features Section
        features_section = models.FeaturesSection.get_solo()
        features_section.eyebrow = "Why Nexus"
        features_section.heading = "Everything a player needs"
        features_section.save()
        self.stdout.write(self.style.SUCCESS("✓ Features section created"))
        
        # Features
        features_data = [
            {
                "key": "booking",
                "icon": "zap",
                "title": "Instant Online Booking",
                "description": "Reserve a court in a few taps, 24/7 — no phone calls, no waiting.",
                "sort_order": 1,
            },
            {
                "key": "availability",
                "icon": "clock",
                "title": "Live Slot Availability",
                "description": "Our real-time calendar shows exactly which hours are open, right now.",
                "sort_order": 2,
            },
            {
                "key": "reschedule",
                "icon": "calendar-clock",
                "title": "Free Rescheduling",
                "description": "Plans change? Reschedule or cancel your slot at no cost up to 12 hours before.",
                "sort_order": 3,
            },
            {
                "key": "tournaments",
                "icon": "trophy",
                "title": "Tournaments & Leagues",
                "description": "Join our regular leagues and knockout nights, with fixtures and standings tracked.",
                "sort_order": 4,
            },
            {
                "key": "coaching",
                "icon": "dumbbell",
                "title": "Coaching & Training",
                "description": "Qualified coaching sessions for kids and adults, mornings and evenings.",
                "sort_order": 5,
            },
            {
                "key": "corporate",
                "icon": "briefcase",
                "title": "Corporate & Events",
                "description": "Book the whole arena for corporate matches, birthdays and private events.",
                "sort_order": 6,
            },
        ]
        for feature in features_data:
            models.FeatureItem.objects.update_or_create(
                key=feature["key"],
                defaults=feature
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(features_data)} features"))
        
        # How It Works Section
        how_it_works = models.HowItWorksSection.get_solo()
        how_it_works.eyebrow = "How it works"
        how_it_works.heading = "On the pitch in three steps"
        how_it_works.save()
        self.stdout.write(self.style.SUCCESS("✓ How it works section created"))
        
        # How It Works Steps
        steps_data = [
            {
                "key": "check",
                "icon": "clock",
                "title": "Check live slots",
                "description": "Open the booking calendar and see exactly which hours are free on each court.",
                "sort_order": 1,
            },
            {
                "key": "reserve",
                "icon": "calendar-check",
                "title": "Reserve your court",
                "description": "Pick your court, date and time — your slot is confirmed instantly.",
                "sort_order": 2,
            },
            {
                "key": "play",
                "icon": "footprints",
                "title": "Show up & play",
                "description": "Settle up at the counter when you arrive and hit the turf. It's that simple.",
                "sort_order": 3,
            },
        ]
        for step in steps_data:
            models.HowItWorksStep.objects.update_or_create(
                key=step["key"],
                defaults=step
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(steps_data)} how-it-works steps"))
        
        # Gallery Preview Section
        gallery = models.GalleryPreviewSection.get_solo()
        gallery.eyebrow = "Gallery"
        gallery.heading = "Straight off our turf"
        gallery.description = "Matches, skills and celebrations from the Nexus community."
        gallery.count_label = "+120 photos"
        gallery.cta_label = "View full gallery"
        gallery.cta_href = "/gallery"
        gallery.cta_style = "outline"
        gallery.save()
        self.stdout.write(self.style.SUCCESS("✓ Gallery preview section created"))
        
        # Testimonials Section
        testimonials_section = models.TestimonialsSection.get_solo()
        testimonials_section.eyebrow = "Testimonials"
        testimonials_section.heading = "What our players say"
        testimonials_section.save()
        self.stdout.write(self.style.SUCCESS("✓ Testimonials section created"))
        
        # Testimonials
        testimonials_data = [
            {
                "key": "t1",
                "quote": "Our squad books the Tuesday 8 PM slot every week. Takes 30 seconds, the turf is always in perfect shape, and the showers are a bonus.",
                "name": "Sujan Tamang",
                "role": "Captain · Kathmandu Kickers",
                "sort_order": 1,
            },
            {
                "key": "t2",
                "quote": "We hosted our company tournament here — bookings, fixtures and the trophy ceremony all handled smoothly. The team genuinely cares.",
                "name": "Priya Shrestha",
                "role": "Organiser · Corporate League",
                "sort_order": 2,
            },
            {
                "key": "t3",
                "quote": "I've been playing here for three years. Best-maintained court in the valley, and the coaching sessions leveled up my son's game.",
                "name": "Kamal Gurung",
                "role": "Weekly regular",
                "sort_order": 3,
            },
            {
                "key": "t4",
                "quote": "Clean facilities, honest pricing and a booking system that actually works. This is how every futsal should be run.",
                "name": "Bibek Maharjan",
                "role": "Sunday league player",
                "sort_order": 4,
            },
        ]
        for testimonial in testimonials_data:
            models.Testimonial.objects.update_or_create(
                key=testimonial["key"],
                defaults=testimonial
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(testimonials_data)} testimonials"))
        
        # CTA Banner Section
        cta = models.CTABannerSection.get_solo()
        cta.heading = "Gather your squad. We'll keep the lights on."
        cta.description = (
            "Book your slot online in under a minute — or drop by the arena and see the turf for yourself."
        )
        cta.primary_cta_label = "Book a Slot"
        cta.primary_cta_href = "/bookings"
        cta.primary_cta_style = "secondary"
        cta.secondary_cta_label = "Contact Us"
        cta.secondary_cta_href = "/contact"
        cta.secondary_cta_style = "outline"
        cta.save()
        self.stdout.write(self.style.SUCCESS("✓ CTA banner section created"))
        
        self.stdout.write(self.style.SUCCESS("\n✅ CMS seeding complete!"))
        self.stdout.write(
            self.style.WARNING(
                "\nNote: Arena images and gallery photos need to be uploaded via Django admin."
            )
        )
        self.stdout.write("Visit /api/v1/cms/homepage/ to see the result.")
