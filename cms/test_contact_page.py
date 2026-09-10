"""Tests for Contact page CMS API."""
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from cms import models

pytestmark = pytest.mark.django_db


@pytest.fixture
def api():
    """API client for unauthenticated requests."""
    return APIClient()


class TestContactPageAPI:
    """Test suite for Contact page CMS endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data for each test."""
        # Create meta
        meta = models.ContactPageMeta.get_solo()
        meta.meta_title = "Contact Us — Nexus FMS"
        meta.meta_description = "Questions about bookings, events or coaching?"
        meta.save()
        
        # Create header
        header = models.ContactHeader.get_solo()
        header.eyebrow = "Contact Us"
        header.title = "We'd love to hear from you"
        header.description = "Booking questions, event plans, a compliment for the groundskeeper."
        header.save()
        
        # Create form
        form = models.ContactForm.get_solo()
        form.heading = "Send us a message"
        form.description = "Fill in the form below."
        form.submit_label = "Send Message"
        form.submitting_label = "Sending…"
        form.success_title = "Message sent!"
        form.success_description = "Thanks {first_name} — we'll reply to {email}."
        form.again_label = "Send another message"
        form.name_label = "Full name"
        form.name_placeholder = "Enter your full name"
        form.email_label = "Email"
        form.email_placeholder = "you@example.com"
        form.phone_label = "Phone number"
        form.phone_placeholder = "10-digit mobile number"
        form.subject_label = "Subject"
        form.subject_placeholder = "e.g. Corporate event"
        form.message_label = "Message"
        form.message_placeholder = "Tell us what's on your mind"
        form.save()
        
        # Create details section
        details = models.ContactDetails.get_solo()
        details.heading = "Reach us directly"
        details.description = "The counter is staffed whenever the lights are on."
        details.maps_label = "Get directions"
        details.save()
        
        # Create detail items
        models.ContactDetailItem.objects.create(
            key="visit",
            item_type="VISIT",
            label="Visit",
            hint="",
            value_source="futsal.address + futsal.location",
            sort_order=1
        )
        models.ContactDetailItem.objects.create(
            key="call",
            item_type="CALL",
            label="Call",
            hint="Fastest way to reach us.",
            value_source="futsal.phone",
            sort_order=2
        )
        
        # Create booking card
        booking_card = models.ContactBookingCard.get_solo()
        booking_card.title = "Looking to book instead?"
        booking_card.description = "Skip the queue."
        booking_card.cta_label = "Book a Slot"
        booking_card.cta_href = "/bookings"
        booking_card.cta_style = "primary"
        booking_card.save()
    
    def test_contact_page_endpoint_exists(self, api):
        """Test that the contact page endpoint is accessible."""
        response = api.get("/api/v1/cms/contact/")
        assert response.status_code == status.HTTP_200_OK
    
    def test_contact_page_response_structure(self, api):
        """Test that response has correct top-level structure."""
        response = api.get("/api/v1/cms/contact/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert "message" in data
    
    def test_contact_page_has_all_sections(self, api):
        """Test that all required sections are present."""
        response = api.get("/api/v1/cms/contact/")
        
        data = response.json()["data"]
        
        # Check all sections exist
        assert "meta_title" in data
        assert "meta_description" in data
        assert "updated_at" in data
        assert "header" in data
        assert "form" in data
        assert "details" in data
        assert "booking_card" in data
    
    def test_header_section_structure(self, api):
        """Test header section has correct structure."""
        response = api.get("/api/v1/cms/contact/")
        
        header = response.json()["data"]["header"]
        
        assert header["eyebrow"] == "Contact Us"
        assert header["title"] == "We'd love to hear from you"
        assert "description" in header
    
    def test_form_section_structure(self, api):
        """Test form section has correct structure."""
        response = api.get("/api/v1/cms/contact/")
        
        form = response.json()["data"]["form"]
        
        assert form["heading"] == "Send us a message"
        assert "description" in form
        assert form["submit_label"] == "Send Message"
        assert form["submitting_label"] == "Sending…"
        assert "fields" in form
        assert "success" in form
        assert form["again_label"] == "Send another message"
    
    def test_form_has_all_fields(self, api):
        """Test form has all required fields."""
        response = api.get("/api/v1/cms/contact/")
        
        fields = response.json()["data"]["form"]["fields"]
        
        # Check all required fields exist
        assert "name" in fields
        assert "email" in fields
        assert "phone_number" in fields
        assert "subject" in fields
        assert "message" in fields
    
    def test_form_field_structure(self, api):
        """Test form field has correct structure."""
        response = api.get("/api/v1/cms/contact/")
        
        name_field = response.json()["data"]["form"]["fields"]["name"]
        
        assert "label" in name_field
        assert "placeholder" in name_field
        assert name_field["label"] == "Full name"
        assert name_field["placeholder"] == "Enter your full name"
    
    def test_form_success_message_structure(self, api):
        """Test form success message has correct structure."""
        response = api.get("/api/v1/cms/contact/")
        
        success = response.json()["data"]["form"]["success"]
        
        assert "title" in success
        assert "description" in success
        assert success["title"] == "Message sent!"
        # Should contain tokens
        assert "{first_name}" in success["description"]
        assert "{email}" in success["description"]
    
    def test_details_section_structure(self, api):
        """Test details section has correct structure."""
        response = api.get("/api/v1/cms/contact/")
        
        details = response.json()["data"]["details"]
        
        assert details["heading"] == "Reach us directly"
        assert "description" in details
        assert details["maps_label"] == "Get directions"
        assert "items" in details
    
    def test_detail_items_structure(self, api):
        """Test detail items have correct structure."""
        response = api.get("/api/v1/cms/contact/")
        
        items = response.json()["data"]["details"]["items"]
        
        assert isinstance(items, list)
        assert len(items) == 2
        
        # Check first item
        visit = items[0]
        assert visit["id"] == "visit"
        assert visit["type"] == "VISIT"
        assert visit["label"] == "Visit"
        assert visit["hint"] is None  # Empty string converted to None
        assert "value_source" in visit
    
    def test_detail_items_ordered_by_sort_order(self, api):
        """Test detail items are ordered by sort_order."""
        response = api.get("/api/v1/cms/contact/")
        
        items = response.json()["data"]["details"]["items"]
        
        # Should be in order: visit (1), call (2)
        assert items[0]["id"] == "visit"
        assert items[1]["id"] == "call"
    
    def test_detail_item_types(self, api):
        """Test detail items have correct types."""
        response = api.get("/api/v1/cms/contact/")
        
        items = response.json()["data"]["details"]["items"]
        
        visit_item = next(item for item in items if item["id"] == "visit")
        call_item = next(item for item in items if item["id"] == "call")
        
        assert visit_item["type"] == "VISIT"
        assert call_item["type"] == "CALL"
    
    def test_detail_item_with_hint(self, api):
        """Test detail item with hint displays correctly."""
        response = api.get("/api/v1/cms/contact/")
        
        items = response.json()["data"]["details"]["items"]
        call_item = next(item for item in items if item["id"] == "call")
        
        assert call_item["hint"] == "Fastest way to reach us."
    
    def test_booking_card_structure(self, api):
        """Test booking card has correct structure."""
        response = api.get("/api/v1/cms/contact/")
        
        card = response.json()["data"]["booking_card"]
        
        assert card["title"] == "Looking to book instead?"
        assert "description" in card
        assert "cta" in card
        
        cta = card["cta"]
        assert cta["label"] == "Book a Slot"
        assert cta["href"] == "/bookings"
        assert cta["style"] == "primary"
    
    def test_inactive_detail_items_excluded(self, api):
        """Test that inactive detail items are excluded."""
        # Create an inactive item
        models.ContactDetailItem.objects.create(
            key="inactive",
            item_type="EMAIL",
            label="Should not appear",
            hint="",
            value_source="test",
            is_active=False,
            sort_order=99
        )
        
        response = api.get("/api/v1/cms/contact/")
        items = response.json()["data"]["details"]["items"]
        
        # Should still have only 2 active items
        assert len(items) == 2
        assert all(item["id"] != "inactive" for item in items)
    
    def test_contact_page_is_public(self, api):
        """Test that contact page is accessible without authentication."""
        response = api.get("/api/v1/cms/contact/")
        
        assert response.status_code == status.HTTP_200_OK
        # Should not require authentication
    
    def test_form_fields_match_api_contract(self, api):
        """Test that form fields match POST /api/v1/contact/ contract."""
        response = api.get("/api/v1/cms/contact/")
        
        fields = response.json()["data"]["form"]["fields"]
        
        # These field names MUST match the contact submission API
        expected_fields = ["name", "email", "phone_number", "subject", "message"]
        
        for field_name in expected_fields:
            assert field_name in fields, f"Missing required field: {field_name}"
        
        # Should have exactly these fields, no more, no less
        assert len(fields) == len(expected_fields)
