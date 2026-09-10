"""Management command to seed CMS with about page content."""
from django.core.management.base import BaseCommand

from cms import models


class Command(BaseCommand):
    help = "Seeds CMS with about page content matching the API contract"

    def handle(self, *args, **options):
        self.stdout.write("Seeding CMS with about page content...")
        
        # About Page Meta
        meta = models.AboutPageMeta.get_solo()
        meta.meta_title = "About Us — Nexus FMS"
        meta.meta_description = (
            "Since 2018, Nexus Futsal has been Kathmandu's home of futsal. "
            "Meet the team, the story and the community behind the turf."
        )
        meta.save()
        self.stdout.write(self.style.SUCCESS("✓ About page meta created"))
        
        # About Hero
        hero = models.AboutHero.get_solo()
        hero.eyebrow = "About us"
        hero.title = "More than a court."
        hero.title_highlight = "A community."
        hero.description = (
            "Since 2018, Nexus Futsal has been Kathmandu's home of futsal — "
            "two meticulously kept courts, floodlights that never quit, and a "
            "community that shows up every single week."
        )
        hero.image_alt = "Players competing in a match at Nexus Futsal"
        hero.save()
        self.stdout.write(self.style.SUCCESS("✓ About hero created"))
        
        # About Stats
        stats_data = [
            {"key": "years", "value": "8+", "label": "Years in the game", "sort_order": 1},
            {"key": "matches", "value": "20K+", "label": "Matches hosted", "sort_order": 2},
            {"key": "tournaments", "value": "150+", "label": "Tournaments run", "sort_order": 3},
            {"key": "players", "value": "12K+", "label": "Players in the community", "sort_order": 4},
        ]
        for stat in stats_data:
            models.AboutStat.objects.update_or_create(
                key=stat["key"],
                defaults=stat
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(stats_data)} stats"))
        
        # About Story
        story = models.AboutStory.get_solo()
        story.eyebrow = "Our story"
        story.heading = "Built by players, for players"
        story.description = (
            "It started with one court, one dream and a lot of late evenings rolling turf. "
            "Eight years later we host everything from 6 AM kickabouts to cup finals under "
            "the floodlights — scroll through the moments that got us here."
        )
        story.timeline_heading = "The journey so far"
        story.timeline_hint = "Drag the cards or use the arrows — the story continues →"
        story.save()
        self.stdout.write(self.style.SUCCESS("✓ About story created"))
        
        # About Milestones
        milestones_data = [
            {
                "key": "2018",
                "year": "2018",
                "title": "One court, one dream",
                "description": "Nexus Futsal opens in Balaju Height with a single court and a borrowed mower.",
                "image_alt": "The original court in 2018",
                "sort_order": 1,
            },
            {
                "key": "2021",
                "year": "2021",
                "title": "The second court",
                "description": "We double down — a second floodlit court, locker rooms and hot showers.",
                "image_alt": "The outdoor court after the expansion",
                "sort_order": 2,
            },
            {
                "key": "2024",
                "year": "2024",
                "title": "Leagues & coaching",
                "description": "Regular tournaments, kids coaching and corporate nights become part of the week.",
                "image_alt": "Kids coaching session on a weekend morning",
                "sort_order": 3,
            },
            {
                "key": "2026",
                "year": "2026",
                "title": "Book online, play more",
                "description": "Real-time online booking launches — your slot is confirmed in seconds.",
                "image_alt": "Match night under the floodlights",
                "sort_order": 4,
            },
        ]
        for milestone in milestones_data:
            models.AboutMilestone.objects.update_or_create(
                key=milestone["key"],
                defaults=milestone
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(milestones_data)} milestones"))
        
        # About Values Section
        values_section = models.AboutValues.get_solo()
        values_section.eyebrow = "What we stand for"
        values_section.heading = "The values on our badge"
        values_section.save()
        self.stdout.write(self.style.SUCCESS("✓ About values section created"))
        
        # About Values
        values_data = [
            {
                "key": "community",
                "icon": "heart-handshake",
                "title": "Community first",
                "description": "We're run by players, for players — regulars, rookies and everyone between.",
                "sort_order": 1,
            },
            {
                "key": "facilities",
                "icon": "sparkles",
                "title": "Facilities without compromise",
                "description": "Turf groomed daily, gear that's actually good, showers that are actually hot.",
                "sort_order": 2,
            },
            {
                "key": "fair-play",
                "icon": "shield-check",
                "title": "Fair play, always",
                "description": "Transparent pricing, honest fixture lists and a red card for bad behaviour.",
                "sort_order": 3,
            },
            {
                "key": "pricing",
                "icon": "wallet",
                "title": "Priced for everyone",
                "description": "Morning rates that make before-work football a habit, not a splurge.",
                "sort_order": 4,
            },
        ]
        for value in values_data:
            models.AboutValue.objects.update_or_create(
                key=value["key"],
                defaults=value
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(values_data)} values"))
        
        # About Community
        community = models.AboutCommunity.get_solo()
        community.eyebrow = "Community"
        community.heading = "The arena fills up long before kickoff"
        community.description = (
            "Futsal is a team game on and off the pitch. Our weeks are packed with leagues, "
            "coaching and nights where strangers leave as teammates."
        )
        community.image_alt = "Coaching session with young players at Nexus Futsal"
        community.save()
        self.stdout.write(self.style.SUCCESS("✓ About community created"))
        
        # About Community Bullets
        bullets_data = [
            {"text": "Weekly leagues for every level — from beginners to the A-division crowd", "sort_order": 1},
            {"text": "Kids coaching on weekend mornings with qualified trainers", "sort_order": 2},
            {"text": "Corporate tournaments and team-building nights", "sort_order": 3},
            {"text": "Open scrimmage nights where solo players find a squad", "sort_order": 4},
        ]
        for bullet in bullets_data:
            models.AboutCommunityBullet.objects.update_or_create(
                text=bullet["text"],
                defaults=bullet
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(bullets_data)} community bullets"))
        
        # About Team Section
        team_section = models.AboutTeam.get_solo()
        team_section.eyebrow = "The team"
        team_section.heading = "The people behind the turf"
        team_section.description = "Say hi when you see us at the counter — we're usually around."
        team_section.save()
        self.stdout.write(self.style.SUCCESS("✓ About team section created"))
        
        # About Team Members
        members_data = [
            {"key": "saroj", "full_name": "Saroj Ghimire", "role": "Founder & Owner", "sort_order": 1},
            {"key": "anisha", "full_name": "Anisha Karki", "role": "Arena Manager", "sort_order": 2},
            {"key": "bikash", "full_name": "Bikash Shrestha", "role": "Head Coach", "sort_order": 3},
            {"key": "rita", "full_name": "Rita Tamang", "role": "Operations", "sort_order": 4},
        ]
        for member in members_data:
            models.AboutTeamMember.objects.update_or_create(
                key=member["key"],
                defaults=member
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(members_data)} team members"))
        
        # About CTA
        cta = models.AboutCTA.get_solo()
        cta.heading = "Come see the turf for yourself"
        cta.description = (
            "Words only get you so far — book a slot, bring your squad and find out why "
            "players keep coming back to Balaju Height."
        )
        cta.primary_cta_label = "Book a Slot"
        cta.primary_cta_href = "/bookings"
        cta.primary_cta_style = "secondary"
        cta.secondary_cta_label = "Contact Us"
        cta.secondary_cta_href = "/contact"
        cta.secondary_cta_style = "outline"
        cta.save()
        self.stdout.write(self.style.SUCCESS("✓ About CTA created"))
        
        self.stdout.write(self.style.SUCCESS("\n✅ About page CMS seeding completed successfully!"))
        self.stdout.write(self.style.WARNING("\n⚠️  Note: Upload images via Django admin for hero, milestones, and community sections."))
