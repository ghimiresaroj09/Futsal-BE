"""CMS tests for gallery page API."""
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
def seed_gallery_content():
    """Seed basic gallery page content for testing."""
    # Meta
    meta = models.GalleryPageMeta.get_solo()
    meta.save()
    
    # Header
    header = models.GalleryHeader.get_solo()
    header.description = "Test description"
    header.save()
    
    # Categories
    models.GalleryCategory.objects.create(key="ALL", label="All", sort_order=1)
    models.GalleryCategory.objects.create(key="VENUE", label="Venue", sort_order=2)
    
    # Photos
    models.GalleryPhoto.objects.create(
        key="test", title="Test", alt_text="Test", category="VENUE", sort_order=1
    )
    
    # Videos Section
    videos_section = models.GalleryVideosSection.get_solo()
    videos_section.save()
    
    # Videos
    models.GalleryVideo.objects.create(
        key="test", title="Test", category="VENUE", duration_seconds=10, sort_order=1
    )
    
    # CTA
    cta = models.GalleryCTA.get_solo()
    cta.description = "Test CTA"
    cta.save()
    
    # Clear cache
    cache.clear()


def test_gallery_page_api_returns_all_sections(api, seed_gallery_content):
    """Test that gallery page API returns all required sections."""
    response = api.get("/api/v1/cms/gallery/")
    
    assert response.status_code == 200
    assert response.data["success"] is True
    
    data = response.data["data"]
    
    # Check all sections exist
    assert "meta_title" in data
    assert "meta_description" in data
    assert "updated_at" in data
    assert "header" in data
    assert "categories" in data
    assert "photos" in data
    assert "videos_section" in data
    assert "cta" in data


def test_gallery_header_structure(api, seed_gallery_content):
    """Test header section has correct structure."""
    response = api.get("/api/v1/cms/gallery/")
    header = response.data["data"]["header"]
    
    assert "eyebrow" in header
    assert "title" in header
    assert "description" in header


def test_gallery_categories_structure(api, seed_gallery_content):
    """Test categories array structure."""
    response = api.get("/api/v1/cms/gallery/")
    categories = response.data["data"]["categories"]
    
    assert isinstance(categories, list)
    assert len(categories) > 0
    
    category = categories[0]
    assert "id" in category
    assert "key" in category
    assert "label" in category


def test_gallery_photos_structure(api, seed_gallery_content):
    """Test photos array structure."""
    response = api.get("/api/v1/cms/gallery/")
    photos = response.data["data"]["photos"]
    
    assert isinstance(photos, list)
    assert len(photos) > 0
    
    photo = photos[0]
    assert "id" in photo
    assert "url" in photo
    assert "alt" in photo
    assert "title" in photo
    assert "category" in photo
    assert "aspect_ratio" in photo


def test_gallery_videos_section_structure(api, seed_gallery_content):
    """Test videos section structure."""
    response = api.get("/api/v1/cms/gallery/")
    videos_section = response.data["data"]["videos_section"]
    
    assert "heading" in videos_section
    assert "description" in videos_section
    assert "videos" in videos_section
    
    videos = videos_section["videos"]
    assert isinstance(videos, list)
    assert len(videos) > 0
    
    video = videos[0]
    assert "id" in video
    assert "url" in video
    assert "poster" in video
    assert "title" in video
    assert "category" in video
    assert "duration_seconds" in video


def test_gallery_cta_structure(api, seed_gallery_content):
    """Test CTA section structure."""
    response = api.get("/api/v1/cms/gallery/")
    cta = response.data["data"]["cta"]
    
    assert "heading" in cta
    assert "description" in cta
    assert "button" in cta
    
    button = cta["button"]
    assert "label" in button
    assert "href" in button
    assert "style" in button


def test_gallery_page_api_is_public(api, seed_gallery_content):
    """Test that gallery page API is accessible without authentication."""
    response = api.get("/api/v1/cms/gallery/")
    assert response.status_code == 200


def test_only_active_items_returned(api, seed_gallery_content):
    """Test that only active items are returned."""
    # Create an inactive photo
    models.GalleryPhoto.objects.create(
        key="inactive", title="Inactive", alt_text="Test", category="VENUE",
        sort_order=999, is_active=False
    )
    
    cache.clear()
    response = api.get("/api/v1/cms/gallery/")
    photos = response.data["data"]["photos"]
    
    # Should not include the inactive item
    photo_keys = [photo["id"] for photo in photos]
    assert "inactive" not in photo_keys


def test_items_ordered_by_sort_order(api, seed_gallery_content):
    """Test that items are returned in sort_order."""
    models.GalleryPhoto.objects.all().delete()
    models.GalleryPhoto.objects.create(
        key="photo3", title="Third", alt_text="3", category="VENUE", sort_order=3
    )
    models.GalleryPhoto.objects.create(
        key="photo1", title="First", alt_text="1", category="VENUE", sort_order=1
    )
    models.GalleryPhoto.objects.create(
        key="photo2", title="Second", alt_text="2", category="VENUE", sort_order=2
    )
    
    cache.clear()
    response = api.get("/api/v1/cms/gallery/")
    photos = response.data["data"]["photos"]
    
    # Should be in sort_order
    assert photos[0]["id"] == "photo1"
    assert photos[1]["id"] == "photo2"
    assert photos[2]["id"] == "photo3"


def test_video_duration_is_integer(api, seed_gallery_content):
    """Test that video duration is returned as integer."""
    response = api.get("/api/v1/cms/gallery/")
    videos = response.data["data"]["videos_section"]["videos"]
    
    for video in videos:
        assert isinstance(video["duration_seconds"], int)


def test_cache_invalidation_on_model_update(api, seed_gallery_content):
    """Test that cache is invalidated when models are updated."""
    # First request - populates cache
    response1 = api.get("/api/v1/cms/gallery/")
    original_title = response1.data["data"]["meta_title"]
    
    # Update model
    meta = models.GalleryPageMeta.get_solo()
    meta.meta_title = "Updated Gallery"
    meta.save()
    
    # Second request - should have new data
    response2 = api.get("/api/v1/cms/gallery/")
    new_title = response2.data["data"]["meta_title"]
    
    assert new_title == "Updated Gallery"
    assert new_title != original_title
