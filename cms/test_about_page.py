"""Tests for About page CMS API."""
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from cms import models

pytestmark = pytest.mark.django_db


@pytest.fixture
def api():
    """API client for unauthenticated requests."""
    return APIClient()


class TestAboutPageAPI:
    """Test suite for About page CMS endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data for each test."""
        # Create meta
        meta = models.AboutPageMeta.get_solo()
        meta.meta_title = "About Us — Nexus FMS"
        meta.meta_description = "Since 2018, Nexus Futsal has been Kathmandu's home of futsal."
        meta.save()
        
        # Create hero
        hero = models.AboutHero.get_solo()
        hero.eyebrow = "About us"
        hero.title = "More than a court."
        hero.title_highlight = "A community."
        hero.description = "Since 2018, Nexus Futsal has been Kathmandu's home of futsal."
        hero.image_alt = "Players competing in a match"
        hero.save()
        
        # Create stats
        models.AboutStat.objects.create(
            key="years",
            value="8+",
            label="Years in the game",
            sort_order=1
        )
        models.AboutStat.objects.create(
            key="matches",
            value="20K+",
            label="Matches hosted",
            sort_order=2
        )
        
        # Create story
        story = models.AboutStory.get_solo()
        story.eyebrow = "Our story"
        story.heading = "Built by players, for players"
        story.description = "It started with one court, one dream."
        story.timeline_heading = "The journey so far"
        story.timeline_hint = "Drag the cards or use the arrows"
        story.save()
        
        # Create milestones
        models.AboutMilestone.objects.create(
            key="2018",
            year="2018",
            title="One court, one dream",
            description="Nexus Futsal opens in Balaju Height.",
            image_alt="The original court",
            sort_order=1
        )
        models.AboutMilestone.objects.create(
            key="2021",
            year="2021",
            title="The second court",
            description="We double down.",
            image_alt="The outdoor court",
            sort_order=2
        )
        
        # Create values section
        values_section = models.AboutValues.get_solo()
        values_section.eyebrow = "What we stand for"
        values_section.heading = "The values on our badge"
        values_section.save()
        
        # Create values
        models.AboutValue.objects.create(
            key="community",
            icon="heart-handshake",
            title="Community first",
            description="We're run by players, for players.",
            sort_order=1
        )
        models.AboutValue.objects.create(
            key="facilities",
            icon="sparkles",
            title="Facilities without compromise",
            description="Turf groomed daily.",
            sort_order=2
        )
        
        # Create community
        community = models.AboutCommunity.get_solo()
        community.eyebrow = "Community"
        community.heading = "The arena fills up long before kickoff"
        community.description = "Futsal is a team game on and off the pitch."
        community.image_alt = "Coaching session with young players"
        community.save()
        
        # Create community bullets
        models.AboutCommunityBullet.objects.create(
            text="Weekly leagues for every level",
            sort_order=1
        )
        models.AboutCommunityBullet.objects.create(
            text="Kids coaching on weekend mornings",
            sort_order=2
        )
        
        # Create team section
        team_section = models.AboutTeam.get_solo()
        team_section.eyebrow = "The team"
        team_section.heading = "The people behind the turf"
        team_section.description = "Say hi when you see us at the counter."
        team_section.save()
        
        # Create team members
        models.AboutTeamMember.objects.create(
            key="saroj",
            full_name="Saroj Ghimire",
            role="Founder & Owner",
            sort_order=1
        )
        models.AboutTeamMember.objects.create(
            key="anisha",
            full_name="Anisha Karki",
            role="Arena Manager",
            sort_order=2
        )
        
        # Create CTA
        cta = models.AboutCTA.get_solo()
        cta.heading = "Come see the turf for yourself"
        cta.description = "Words only get you so far."
        cta.primary_cta_label = "Book a Slot"
        cta.primary_cta_href = "/bookings"
        cta.primary_cta_style = "secondary"
        cta.secondary_cta_label = "Contact Us"
        cta.secondary_cta_href = "/contact"
        cta.secondary_cta_style = "outline"
        cta.save()
    
    def test_about_page_endpoint_exists(self, api):
        """Test that the about page endpoint is accessible."""
        response = api.get("/api/v1/cms/about/")
        assert response.status_code == status.HTTP_200_OK
    
    def test_about_page_response_structure(self, api):
        """Test that response has correct top-level structure."""
        
        response = api.get("/api/v1/cms/about/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert "message" in data
    
    def test_about_page_has_all_sections(self, api):
        """Test that all required sections are present."""
        
        response = api.get("/api/v1/cms/about/")
        
        data = response.json()["data"]
        
        # Check all sections exist
        assert "meta_title" in data
        assert "meta_description" in data
        assert "updated_at" in data
        assert "hero" in data
        assert "stats" in data
        assert "story" in data
        assert "values" in data
        assert "community" in data
        assert "team" in data
        assert "cta_banner" in data
    
    def test_hero_section_structure(self, api):
        """Test hero section has correct structure."""
        
        response = api.get("/api/v1/cms/about/")
        
        hero = response.json()["data"]["hero"]
        
        assert hero["eyebrow"] == "About us"
        assert hero["title"] == "More than a court."
        assert hero["title_highlight"] == "A community."
        assert "description" in hero
        assert "image" in hero
        assert "url" in hero["image"]
        assert "alt" in hero["image"]
    
    def test_stats_section(self, api):
        """Test stats section returns list of 2 stats."""
        
        response = api.get("/api/v1/cms/about/")
        
        stats = response.json()["data"]["stats"]
        
        assert isinstance(stats, list)
        assert len(stats) == 2
        
        # Check first stat structure
        stat = stats[0]
        assert stat["id"] == "years"
        assert stat["value"] == "8+"
        assert stat["label"] == "Years in the game"
    
    def test_story_section_with_milestones(self, api):
        """Test story section includes milestones."""
        
        response = api.get("/api/v1/cms/about/")
        
        story = response.json()["data"]["story"]
        
        assert story["eyebrow"] == "Our story"
        assert story["heading"] == "Built by players, for players"
        assert "description" in story
        assert story["timeline_heading"] == "The journey so far"
        assert "timeline_hint" in story
        assert "milestones" in story
        
        # Check milestones
        milestones = story["milestones"]
        assert isinstance(milestones, list)
        assert len(milestones) == 2
        
        # Check first milestone
        milestone = milestones[0]
        assert milestone["id"] == "2018"
        assert milestone["year"] == "2018"
        assert milestone["title"] == "One court, one dream"
        assert "description" in milestone
        assert "image" in milestone
    
    def test_values_section(self, api):
        """Test values section structure."""
        
        response = api.get("/api/v1/cms/about/")
        
        values = response.json()["data"]["values"]
        
        assert values["eyebrow"] == "What we stand for"
        assert values["heading"] == "The values on our badge"
        assert "items" in values
        
        # Check values items
        items = values["items"]
        assert isinstance(items, list)
        assert len(items) == 2
        
        # Check first value
        value = items[0]
        assert value["id"] == "community"
        assert value["icon"] == "heart-handshake"
        assert value["title"] == "Community first"
        assert "description" in value
    
    def test_community_section_with_bullets(self, api):
        """Test community section includes bullets."""
        
        response = api.get("/api/v1/cms/about/")
        
        community = response.json()["data"]["community"]
        
        assert community["eyebrow"] == "Community"
        assert community["heading"] == "The arena fills up long before kickoff"
        assert "description" in community
        assert "bullets" in community
        assert "image" in community
        
        # Check bullets
        bullets = community["bullets"]
        assert isinstance(bullets, list)
        assert len(bullets) == 2
        assert bullets[0] == "Weekly leagues for every level"
        assert bullets[1] == "Kids coaching on weekend mornings"
    
    def test_team_section_with_members(self, api):
        """Test team section includes members."""
        
        response = api.get("/api/v1/cms/about/")
        
        team = response.json()["data"]["team"]
        
        assert team["eyebrow"] == "The team"
        assert team["heading"] == "The people behind the turf"
        assert "description" in team
        assert "members" in team
        
        # Check members
        members = team["members"]
        assert isinstance(members, list)
        assert len(members) == 2
        
        # Check first member
        member = members[0]
        assert member["id"] == "saroj"
        assert member["full_name"] == "Saroj Ghimire"
        assert member["role"] == "Founder & Owner"
        assert member["profile_image"] is None  # No image uploaded
    
    def test_cta_banner_section(self, api):
        """Test CTA banner section structure."""
        
        response = api.get("/api/v1/cms/about/")
        
        cta = response.json()["data"]["cta_banner"]
        
        assert cta["heading"] == "Come see the turf for yourself"
        assert "description" in cta
        assert "primary_cta" in cta
        assert "secondary_cta" in cta
        
        # Check primary CTA
        primary = cta["primary_cta"]
        assert primary["label"] == "Book a Slot"
        assert primary["href"] == "/bookings"
        assert primary["style"] == "secondary"
        
        # Check secondary CTA
        secondary = cta["secondary_cta"]
        assert secondary["label"] == "Contact Us"
        assert secondary["href"] == "/contact"
        assert secondary["style"] == "outline"
    
    def test_inactive_items_excluded(self, api):
        """Test that inactive items are excluded from response."""
        # Create an inactive stat
        models.AboutStat.objects.create(
            key="inactive",
            value="999",
            label="Should not appear",
            is_active=False,
            sort_order=99
        )
        
        
        response = api.get("/api/v1/cms/about/")
        
        stats = response.json()["data"]["stats"]
        
        # Should still have only 2 active stats
        assert len(stats) == 2
        assert all(stat["id"] != "inactive" for stat in stats)
    
    def test_items_ordered_by_sort_order(self, api):
        """Test that items are ordered by sort_order field."""
        
        response = api.get("/api/v1/cms/about/")
        
        stats = response.json()["data"]["stats"]
        
        # Check order
        assert stats[0]["id"] == "years"  # sort_order=1
        assert stats[1]["id"] == "matches"  # sort_order=2
    
    def test_about_page_is_public(self, api):
        """Test that about page is accessible without authentication."""
        
        response = api.get("/api/v1/cms/about/")
        
        assert response.status_code == status.HTTP_200_OK
        # Should not require authentication
