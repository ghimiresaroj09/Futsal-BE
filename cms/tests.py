"""CMS tests for homepage API."""
import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from cms import models

pytestmark = pytest.mark.django_db


@pytest.fixture
def api():
    """API client for unauthenticated requests."""
    return APIClient()


@pytest.fixture
def seed_cms_content():
    """Seed basic CMS content for testing."""
    # Meta
    meta = models.HomepageMeta.get_solo()
    meta.meta_title = "Test Futsal"
    meta.meta_description = "Test description"
    meta.save()
    
    # Hero
    hero = models.HeroSection.get_solo()
    hero.badge = "Test badge"
    hero.title = "Test title"
    hero.description = "Test description"
    hero.save()
    
    # Stats
    models.StatItem.objects.create(key="test1", value="10", label="Test stat", sort_order=1)
    
    # Arena
    arena = models.ArenaSection.get_solo()
    arena.description = "Test arena"
    arena.save()
    
    models.ArenaHighlight.objects.create(
        key="test", icon="test", text="Test highlight", sort_order=1
    )
    
    # Features
    features = models.FeaturesSection.get_solo()
    features.save()
    
    models.FeatureItem.objects.create(
        key="test", icon="test", title="Test", description="Test", sort_order=1
    )
    
    # How it works
    how_it_works = models.HowItWorksSection.get_solo()
    how_it_works.save()
    
    models.HowItWorksStep.objects.create(
        key="test", icon="test", title="Test", description="Test", sort_order=1
    )
    
    # Gallery
    gallery = models.GalleryPreviewSection.get_solo()
    gallery.description = "Test gallery"
    gallery.save()
    
    # Testimonials
    testimonials = models.TestimonialsSection.get_solo()
    testimonials.save()
    
    models.Testimonial.objects.create(
        key="test", quote="Test quote", name="Test Name", role="Test Role", sort_order=1
    )
    
    # CTA
    cta = models.CTABannerSection.get_solo()
    cta.description = "Test CTA"
    cta.save()
    
    # Clear cache
    cache.clear()


def test_homepage_api_returns_all_sections(api, seed_cms_content):
    """Test that homepage API returns all required sections."""
    response = api.get("/api/v1/cms/homepage/")
    
    assert response.status_code == 200
    assert response.data["success"] is True
    
    data = response.data["data"]
    
    # Check all sections exist
    assert "meta_title" in data
    assert "meta_description" in data
    assert "updated_at" in data
    assert "hero" in data
    assert "stats" in data
    assert "arena" in data
    assert "features" in data
    assert "how_it_works" in data
    assert "gallery_preview" in data
    assert "testimonials" in data
    assert "cta_banner" in data


def test_homepage_hero_section_structure(api, seed_cms_content):
    """Test hero section has correct structure."""
    response = api.get("/api/v1/cms/homepage/")
    hero = response.data["data"]["hero"]
    
    assert "badge" in hero
    assert "title" in hero
    assert "title_highlight" in hero
    assert "description" in hero
    assert "image" in hero
    assert "primary_cta" in hero
    assert "secondary_cta" in hero
    
    # Check image structure
    assert "url" in hero["image"]
    assert "alt" in hero["image"]
    
    # Check CTA structure
    assert "label" in hero["primary_cta"]
    assert "href" in hero["primary_cta"]
    assert "style" in hero["primary_cta"]


def test_homepage_stats_array(api, seed_cms_content):
    """Test stats are returned as an array."""
    response = api.get("/api/v1/cms/homepage/")
    stats = response.data["data"]["stats"]
    
    assert isinstance(stats, list)
    assert len(stats) > 0
    
    stat = stats[0]
    assert "id" in stat
    assert "value" in stat
    assert "label" in stat


def test_homepage_arena_section_structure(api, seed_cms_content):
    """Test arena section has correct structure."""
    response = api.get("/api/v1/cms/homepage/")
    arena = response.data["data"]["arena"]
    
    assert "eyebrow" in arena
    assert "heading" in arena
    assert "description" in arena
    assert "since_label" in arena
    assert "highlights" in arena
    assert "images" in arena
    
    assert isinstance(arena["highlights"], list)
    assert isinstance(arena["images"], list)


def test_homepage_features_section_structure(api, seed_cms_content):
    """Test features section has correct structure."""
    response = api.get("/api/v1/cms/homepage/")
    features = response.data["data"]["features"]
    
    assert "eyebrow" in features
    assert "heading" in features
    assert "items" in features
    
    assert isinstance(features["items"], list)
    assert len(features["items"]) > 0
    
    item = features["items"][0]
    assert "id" in item
    assert "icon" in item
    assert "title" in item
    assert "description" in item


def test_homepage_how_it_works_structure(api, seed_cms_content):
    """Test how it works section has correct structure."""
    response = api.get("/api/v1/cms/homepage/")
    how_it_works = response.data["data"]["how_it_works"]
    
    assert "eyebrow" in how_it_works
    assert "heading" in how_it_works
    assert "steps" in how_it_works
    
    assert isinstance(how_it_works["steps"], list)


def test_homepage_gallery_preview_structure(api, seed_cms_content):
    """Test gallery preview section has correct structure."""
    response = api.get("/api/v1/cms/homepage/")
    gallery = response.data["data"]["gallery_preview"]
    
    assert "eyebrow" in gallery
    assert "heading" in gallery
    assert "description" in gallery
    assert "count_label" in gallery
    assert "cta" in gallery
    assert "photos" in gallery
    
    assert isinstance(gallery["photos"], list)


def test_homepage_testimonials_structure(api, seed_cms_content):
    """Test testimonials section has correct structure."""
    response = api.get("/api/v1/cms/homepage/")
    testimonials = response.data["data"]["testimonials"]
    
    assert "eyebrow" in testimonials
    assert "heading" in testimonials
    assert "items" in testimonials
    
    assert isinstance(testimonials["items"], list)
    assert len(testimonials["items"]) > 0
    
    item = testimonials["items"][0]
    assert "id" in item
    assert "quote" in item
    assert "name" in item
    assert "role" in item
    assert "avatar" in item


def test_homepage_cta_banner_structure(api, seed_cms_content):
    """Test CTA banner section has correct structure."""
    response = api.get("/api/v1/cms/homepage/")
    cta = response.data["data"]["cta_banner"]
    
    assert "heading" in cta
    assert "description" in cta
    assert "primary_cta" in cta
    assert "secondary_cta" in cta


def test_homepage_api_is_public(api, seed_cms_content):
    """Test that homepage API is accessible without authentication."""
    response = api.get("/api/v1/cms/homepage/")
    assert response.status_code == 200


def test_only_active_items_returned(api, seed_cms_content):
    """Test that only active items are returned."""
    # Create an inactive stat
    models.StatItem.objects.create(
        key="inactive", value="99", label="Inactive", sort_order=999, is_active=False
    )
    
    cache.clear()
    response = api.get("/api/v1/cms/homepage/")
    stats = response.data["data"]["stats"]
    
    # Should not include the inactive item
    stat_keys = [stat["id"] for stat in stats]
    assert "inactive" not in stat_keys


def test_items_ordered_by_sort_order(api, seed_cms_content):
    """Test that items are returned in sort_order."""
    models.StatItem.objects.all().delete()
    models.StatItem.objects.create(key="stat3", value="3", label="Third", sort_order=3)
    models.StatItem.objects.create(key="stat1", value="1", label="First", sort_order=1)
    models.StatItem.objects.create(key="stat2", value="2", label="Second", sort_order=2)
    
    cache.clear()
    response = api.get("/api/v1/cms/homepage/")
    stats = response.data["data"]["stats"]
    
    # Should be in sort_order
    assert stats[0]["id"] == "stat1"
    assert stats[1]["id"] == "stat2"
    assert stats[2]["id"] == "stat3"


def test_cache_invalidation_on_model_update(api, seed_cms_content):
    """Test that cache is invalidated when models are updated."""
    # First request - populates cache
    response1 = api.get("/api/v1/cms/homepage/")
    original_title = response1.data["data"]["meta_title"]
    
    # Update model
    meta = models.HomepageMeta.get_solo()
    meta.meta_title = "Updated Title"
    meta.save()
    
    # Second request - should have new data
    response2 = api.get("/api/v1/cms/homepage/")
    new_title = response2.data["data"]["meta_title"]
    
    assert new_title == "Updated Title"
    assert new_title != original_title
