"""CMS tests for bookings page API."""
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
def seed_bookings_content():
    """Seed basic bookings page content for testing."""
    # Meta
    meta = models.BookingsPageMeta.get_solo()
    meta.meta_title = "Test Bookings"
    meta.meta_description = "Test description"
    meta.save()
    
    # Banner
    banner = models.BookingsBanner.get_solo()
    banner.title = "Test title"
    banner.description = "Test description"
    banner.save()
    
    # Steps
    steps_section = models.BookingsStepsSection.get_solo()
    steps_section.save()
    
    models.BookingsStep.objects.create(
        key="test", title="Test Step", description="Test", sort_order=1
    )
    
    # Rates
    rates_section = models.BookingsRatesSection.get_solo()
    rates_section.description = "Test rates"
    rates_section.refreshments_note = "Test note"
    rates_section.save()
    
    models.BookingsRateRow.objects.create(
        key="test", title="Test", hours="1-2 PM", 
        weekday_price=1000, weekend_price=1200, sort_order=1
    )
    
    # Policies
    policies_section = models.BookingsPoliciesSection.get_solo()
    policies_section.save()
    
    models.BookingsPolicy.objects.create(
        key="test", icon="test", title="Test", description="Test", sort_order=1
    )
    
    # Help strip
    help_strip = models.BookingsHelpStrip.get_solo()
    help_strip.description = "Test help"
    help_strip.save()
    
    # Clear cache
    cache.clear()


def test_bookings_page_api_returns_all_sections(api, seed_bookings_content):
    """Test that bookings page API returns all required sections."""
    response = api.get("/api/v1/cms/bookings/")
    
    assert response.status_code == 200
    assert response.data["success"] is True
    
    data = response.data["data"]
    
    # Check all sections exist
    assert "meta_title" in data
    assert "meta_description" in data
    assert "updated_at" in data
    assert "banner" in data
    assert "steps" in data
    assert "rates" in data
    assert "policies" in data
    assert "help_strip" in data


def test_bookings_banner_structure(api, seed_bookings_content):
    """Test banner section has correct structure."""
    response = api.get("/api/v1/cms/bookings/")
    banner = response.data["data"]["banner"]
    
    assert "eyebrow" in banner
    assert "title" in banner
    assert "description" in banner
    assert "image" in banner
    
    # Check image structure
    assert "url" in banner["image"]
    assert "alt" in banner["image"]


def test_bookings_steps_structure(api, seed_bookings_content):
    """Test steps section has correct structure."""
    response = api.get("/api/v1/cms/bookings/")
    steps = response.data["data"]["steps"]
    
    assert "heading" in steps
    assert "items" in steps
    assert isinstance(steps["items"], list)
    assert len(steps["items"]) > 0
    
    item = steps["items"][0]
    assert "id" in item
    assert "title" in item
    assert "description" in item


def test_bookings_rates_structure(api, seed_bookings_content):
    """Test rates section has correct structure."""
    response = api.get("/api/v1/cms/bookings/")
    rates = response.data["data"]["rates"]
    
    assert "heading" in rates
    assert "description" in rates
    assert "weekday_label" in rates
    assert "weekend_label" in rates
    assert "rows" in rates
    assert "events" in rates
    assert "refreshments_note" in rates
    
    # Check rows structure
    assert isinstance(rates["rows"], list)
    assert len(rates["rows"]) > 0
    
    row = rates["rows"][0]
    assert "id" in row
    assert "title" in row
    assert "hours" in row
    assert "weekday_price" in row
    assert "weekend_price" in row
    assert "highlight" in row
    assert "highlight_label" in row
    
    # Check events structure
    events = rates["events"]
    assert "title" in events
    assert "description" in events
    assert "cta" in events


def test_bookings_policies_structure(api, seed_bookings_content):
    """Test policies section has correct structure."""
    response = api.get("/api/v1/cms/bookings/")
    policies = response.data["data"]["policies"]
    
    assert "heading" in policies
    assert "items" in policies
    assert isinstance(policies["items"], list)
    assert len(policies["items"]) > 0
    
    item = policies["items"][0]
    assert "id" in item
    assert "icon" in item
    assert "title" in item
    assert "description" in item


def test_bookings_help_strip_structure(api, seed_bookings_content):
    """Test help strip section has correct structure."""
    response = api.get("/api/v1/cms/bookings/")
    help_strip = response.data["data"]["help_strip"]
    
    assert "heading" in help_strip
    assert "description" in help_strip
    assert "cta" in help_strip
    
    cta = help_strip["cta"]
    assert "label" in cta
    assert "href" in cta
    assert "style" in cta


def test_bookings_page_api_is_public(api, seed_bookings_content):
    """Test that bookings page API is accessible without authentication."""
    response = api.get("/api/v1/cms/bookings/")
    assert response.status_code == 200


def test_only_active_items_returned(api, seed_bookings_content):
    """Test that only active items are returned."""
    # Create an inactive step
    models.BookingsStep.objects.create(
        key="inactive", title="Inactive", description="Test", 
        sort_order=999, is_active=False
    )
    
    cache.clear()
    response = api.get("/api/v1/cms/bookings/")
    steps = response.data["data"]["steps"]["items"]
    
    # Should not include the inactive item
    step_keys = [step["id"] for step in steps]
    assert "inactive" not in step_keys


def test_items_ordered_by_sort_order(api, seed_bookings_content):
    """Test that items are returned in sort_order."""
    models.BookingsStep.objects.all().delete()
    models.BookingsStep.objects.create(
        key="step3", title="Third", description="3", sort_order=3
    )
    models.BookingsStep.objects.create(
        key="step1", title="First", description="1", sort_order=1
    )
    models.BookingsStep.objects.create(
        key="step2", title="Second", description="2", sort_order=2
    )
    
    cache.clear()
    response = api.get("/api/v1/cms/bookings/")
    steps = response.data["data"]["steps"]["items"]
    
    # Should be in sort_order
    assert steps[0]["id"] == "step1"
    assert steps[1]["id"] == "step2"
    assert steps[2]["id"] == "step3"


def test_rate_row_prices_are_integers(api, seed_bookings_content):
    """Test that rate row prices are returned as integers."""
    response = api.get("/api/v1/cms/bookings/")
    rows = response.data["data"]["rates"]["rows"]
    
    for row in rows:
        assert isinstance(row["weekday_price"], int)
        assert isinstance(row["weekend_price"], int)


def test_cache_invalidation_on_model_update(api, seed_bookings_content):
    """Test that cache is invalidated when models are updated."""
    # First request - populates cache
    response1 = api.get("/api/v1/cms/bookings/")
    original_title = response1.data["data"]["meta_title"]
    
    # Update model
    meta = models.BookingsPageMeta.get_solo()
    meta.meta_title = "Updated Title"
    meta.save()
    
    # Second request - should have new data
    response2 = api.get("/api/v1/cms/bookings/")
    new_title = response2.data["data"]["meta_title"]
    
    assert new_title == "Updated Title"
    assert new_title != original_title


def test_highlighted_rate_row(api, seed_bookings_content):
    """Test that highlighted rate rows include highlight info."""
    models.BookingsRateRow.objects.create(
        key="highlighted", title="Premium", hours="8-10 PM",
        weekday_price=3000, weekend_price=3500,
        highlight=True, highlight_label="Peak Hours",
        sort_order=2
    )
    
    cache.clear()
    response = api.get("/api/v1/cms/bookings/")
    rows = response.data["data"]["rates"]["rows"]
    
    # Find the highlighted row
    highlighted = next((r for r in rows if r["id"] == "highlighted"), None)
    assert highlighted is not None
    assert highlighted["highlight"] is True
    assert highlighted["highlight_label"] == "Peak Hours"
