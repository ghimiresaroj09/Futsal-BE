"""Management command to seed CMS with gallery page content."""
from django.core.management.base import BaseCommand

from cms import models


class Command(BaseCommand):
    help = "Seeds CMS with gallery page content matching the API contract"

    def handle(self, *args, **options):
        self.stdout.write("Seeding CMS with gallery page content...")
        
        # Gallery Page Meta
        meta = models.GalleryPageMeta.get_solo()
        meta.meta_title = "Gallery — Nexus FMS"
        meta.meta_description = (
            "Photos and clips from the Nexus Futsal community — match nights, "
            "coaching mornings and the turf itself."
        )
        meta.save()
        self.stdout.write(self.style.SUCCESS("✓ Gallery page meta created"))
        
        # Gallery Header
        header = models.GalleryHeader.get_solo()
        header.eyebrow = "Gallery"
        header.title = "The arena, up close"
        header.description = (
            "Match nights, coaching mornings and the turf itself — a little eye candy "
            "from around Nexus. It looks even better in person."
        )
        header.save()
        self.stdout.write(self.style.SUCCESS("✓ Gallery header created"))
        
        # Gallery Categories
        categories_data = [
            {"key": "ALL", "label": "All", "sort_order": 1},
            {"key": "VENUE", "label": "Our Venue", "sort_order": 2},
            {"key": "MATCHES", "label": "Match Nights", "sort_order": 3},
            {"key": "COMMUNITY", "label": "Community", "sort_order": 4},
        ]
        for category in categories_data:
            models.GalleryCategory.objects.update_or_create(
                key=category["key"],
                defaults=category
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(categories_data)} categories"))
        
        # Gallery Photos (examples - need image uploads via admin)
        photos_data = [
            {
                "key": "hero",
                "title": "Kickoff under the lights",
                "alt_text": "Kickoff under the lights",
                "category": "MATCHES",
                "aspect_ratio": "16/10",
                "sort_order": 1,
            },
            {
                "key": "venue-indoor",
                "title": "The indoor court",
                "alt_text": "The indoor court",
                "category": "VENUE",
                "aspect_ratio": "3/4",
                "sort_order": 2,
            },
            {
                "key": "action-2",
                "title": "Midfield battle",
                "alt_text": "Midfield battle",
                "category": "MATCHES",
                "aspect_ratio": "1/1",
                "sort_order": 3,
            },
            {
                "key": "floodlights",
                "title": "Floodlights on",
                "alt_text": "Floodlights on",
                "category": "VENUE",
                "aspect_ratio": "4/5",
                "sort_order": 4,
            },
            {
                "key": "celebration",
                "title": "That goal feeling",
                "alt_text": "That goal feeling",
                "category": "COMMUNITY",
                "aspect_ratio": "4/3",
                "sort_order": 5,
            },
            {
                "key": "venue-outdoor",
                "title": "The outdoor court",
                "alt_text": "The outdoor court",
                "category": "VENUE",
                "aspect_ratio": "4/3",
                "sort_order": 6,
            },
            {
                "key": "action-1",
                "title": "Saved!",
                "alt_text": "Saved!",
                "category": "MATCHES",
                "aspect_ratio": "4/3",
                "sort_order": 7,
            },
            {
                "key": "coaching",
                "title": "Saturday coaching",
                "alt_text": "Saturday coaching",
                "category": "COMMUNITY",
                "aspect_ratio": "3/4",
                "sort_order": 8,
            },
            {
                "key": "turf",
                "title": "Fresh turf, morning light",
                "alt_text": "Fresh turf, morning light",
                "category": "VENUE",
                "aspect_ratio": "1/1",
                "sort_order": 9,
            },
            {
                "key": "venue-rooftop",
                "title": "Court with a view",
                "alt_text": "Court with a view",
                "category": "VENUE",
                "aspect_ratio": "16/10",
                "sort_order": 10,
            },
        ]
        
        # Only create photo records if they don't exist (images need manual upload)
        for photo in photos_data:
            models.GalleryPhoto.objects.get_or_create(
                key=photo["key"],
                defaults=photo
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(photos_data)} photo records"))
        
        # Gallery Videos Section
        videos_section = models.GalleryVideosSection.get_solo()
        videos_section.heading = "Highlights & clips"
        videos_section.description = "Short clips from around the arena — press play."
        videos_section.save()
        self.stdout.write(self.style.SUCCESS("✓ Gallery videos section created"))
        
        # Gallery Videos (examples - need video/poster uploads via admin)
        videos_data = [
            {
                "key": "v-floodlights",
                "title": "Floodlights on at dusk",
                "category": "VENUE",
                "duration_seconds": 6,
                "sort_order": 1,
            },
            {
                "key": "v-action",
                "title": "Match night intensity",
                "category": "MATCHES",
                "duration_seconds": 6,
                "sort_order": 2,
            },
            {
                "key": "v-coaching",
                "title": "Little legs, big dreams",
                "category": "COMMUNITY",
                "duration_seconds": 6,
                "sort_order": 3,
            },
        ]
        
        # Only create video records if they don't exist (videos need manual upload)
        for video in videos_data:
            models.GalleryVideo.objects.get_or_create(
                key=video["key"],
                defaults=video
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(videos_data)} video records"))
        
        # Gallery CTA
        cta = models.GalleryCTA.get_solo()
        cta.heading = "Pictures are nice. Playing is nicer."
        cta.description = "Grab a slot, bring your squad and make your own highlight reel."
        cta.button_label = "Book a Slot"
        cta.button_href = "/bookings"
        cta.button_style = "primary"
        cta.save()
        self.stdout.write(self.style.SUCCESS("✓ Gallery CTA created"))
        
        self.stdout.write(self.style.SUCCESS("\n✅ Gallery page CMS seeding complete!"))
        self.stdout.write(
            self.style.WARNING(
                "\nNote: Photos and videos need to be uploaded via Django admin."
            )
        )
        self.stdout.write(
            self.style.WARNING(
                "Photo/video records have been created - upload files for each one."
            )
        )
        self.stdout.write("Visit /api/v1/cms/gallery/ to see the result.")
