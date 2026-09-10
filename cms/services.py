"""CMS services for updating content."""
from __future__ import annotations

from typing import Any

from django.db import transaction

from cms import models
from cms.selectors import (
    invalidate_about_page_cache,
    invalidate_bookings_page_cache,
    invalidate_contact_page_cache,
    invalidate_gallery_page_cache,
    invalidate_homepage_cache,
)


@transaction.atomic
def update_homepage_content(data: dict[str, Any]) -> dict[str, Any]:
    """
    Update homepage content from provided data.
    
    Updates all singleton sections and manages list items (stats, features, etc.).
    Invalidates cache after successful update.
    
    Args:
        data: Dictionary matching HomepageSerializer structure
        
    Returns:
        Updated homepage data
    """
    # Update Meta
    if "meta_title" in data or "meta_description" in data:
        meta = models.HomepageMeta.get_solo()
        if "meta_title" in data:
            meta.meta_title = data["meta_title"]
        if "meta_description" in data:
            meta.meta_description = data["meta_description"]
        meta.save()
    
    # Update Hero
    if "hero" in data:
        hero = models.HeroSection.get_solo()
        hero_data = data["hero"]
        for field in ["badge", "title", "title_highlight", "description", "image_alt",
                      "primary_cta_label", "primary_cta_href", "primary_cta_style",
                      "secondary_cta_label", "secondary_cta_href", "secondary_cta_style"]:
            if field in hero_data:
                setattr(hero, field, hero_data[field])
        hero.save()
    
    # Update Stats (replace all)
    if "stats" in data:
        models.StatItem.objects.all().delete()
        for idx, stat in enumerate(data["stats"]):
            models.StatItem.objects.create(
                key=stat.get("id", f"stat_{idx}"),
                value=stat["value"],
                label=stat["label"],
                sort_order=idx + 1
            )
    
    invalidate_homepage_cache()
    
    from cms.selectors import get_homepage_data
    return get_homepage_data()


@transaction.atomic
def update_bookings_page_content(data: dict[str, Any]) -> dict[str, Any]:
    """Update bookings page content from provided data."""
    # Update Meta
    if "meta_title" in data or "meta_description" in data:
        meta = models.BookingsPageMeta.get_solo()
        if "meta_title" in data:
            meta.meta_title = data["meta_title"]
        if "meta_description" in data:
            meta.meta_description = data["meta_description"]
        meta.save()
    
    # Update Banner
    if "banner" in data:
        banner = models.BookingsBanner.get_solo()
        banner_data = data["banner"]
        for field in ["eyebrow", "title", "description", "image_alt"]:
            if field in banner_data:
                setattr(banner, field, banner_data[field])
        banner.save()
    
    # Update Steps Section
    if "steps" in data:
        section = models.BookingsStepsSection.get_solo()
        if "heading" in data["steps"]:
            section.heading = data["steps"]["heading"]
        section.save()
        
        # Update steps items
        if "items" in data["steps"]:
            models.BookingsStep.objects.all().delete()
            for idx, step in enumerate(data["steps"]["items"]):
                models.BookingsStep.objects.create(
                    key=step.get("id", f"step_{idx}"),
                    title=step["title"],
                    description=step["description"],
                    sort_order=idx + 1
                )
    
    invalidate_bookings_page_cache()
    
    from cms.selectors import get_bookings_page_data
    return get_bookings_page_data()


@transaction.atomic
def update_gallery_page_content(data: dict[str, Any]) -> dict[str, Any]:
    """Update gallery page content from provided data."""
    # Update Meta
    if "meta_title" in data or "meta_description" in data:
        meta = models.GalleryPageMeta.get_solo()
        if "meta_title" in data:
            meta.meta_title = data["meta_title"]
        if "meta_description" in data:
            meta.meta_description = data["meta_description"]
        meta.save()
    
    # Update Header
    if "header" in data:
        header = models.GalleryHeader.get_solo()
        header_data = data["header"]
        for field in ["eyebrow", "title", "description"]:
            if field in header_data:
                setattr(header, field, header_data[field])
        header.save()
    
    # Update Categories
    if "categories" in data:
        models.GalleryCategory.objects.all().delete()
        for idx, category in enumerate(data["categories"]):
            models.GalleryCategory.objects.create(
                key=category.get("key", category.get("id")),
                label=category["label"],
                sort_order=idx + 1
            )
    
    invalidate_gallery_page_cache()
    
    from cms.selectors import get_gallery_page_data
    return get_gallery_page_data()


@transaction.atomic
def update_about_page_content(data: dict[str, Any]) -> dict[str, Any]:
    """Update about page content from provided data."""
    # Update Meta
    if "meta_title" in data or "meta_description" in data:
        meta = models.AboutPageMeta.get_solo()
        if "meta_title" in data:
            meta.meta_title = data["meta_title"]
        if "meta_description" in data:
            meta.meta_description = data["meta_description"]
        meta.save()
    
    # Update Hero
    if "hero" in data:
        hero = models.AboutHero.get_solo()
        hero_data = data["hero"]
        for field in ["eyebrow", "title", "title_highlight", "description", "image_alt"]:
            if field in hero_data:
                setattr(hero, field, hero_data[field])
        hero.save()
    
    # Update Stats
    if "stats" in data:
        models.AboutStat.objects.all().delete()
        for idx, stat in enumerate(data["stats"]):
            models.AboutStat.objects.create(
                key=stat.get("id", f"stat_{idx}"),
                value=stat["value"],
                label=stat["label"],
                sort_order=idx + 1
            )
    
    # Update Story Section
    if "story" in data:
        story = models.AboutStory.get_solo()
        story_data = data["story"]
        for field in ["eyebrow", "heading", "description", "timeline_heading", "timeline_hint"]:
            if field in story_data:
                setattr(story, field, story_data[field])
        story.save()
        
        # Update milestones
        if "milestones" in story_data:
            models.AboutMilestone.objects.all().delete()
            for idx, milestone in enumerate(story_data["milestones"]):
                models.AboutMilestone.objects.create(
                    key=milestone.get("id", f"milestone_{idx}"),
                    year=milestone["year"],
                    title=milestone["title"],
                    description=milestone["description"],
                    image_alt=milestone.get("image", {}).get("alt", ""),
                    sort_order=idx + 1
                )
    
    # Update Values Section
    if "values" in data:
        values = models.AboutValues.get_solo()
        values_data = data["values"]
        if "eyebrow" in values_data:
            values.eyebrow = values_data["eyebrow"]
        if "heading" in values_data:
            values.heading = values_data["heading"]
        values.save()
        
        # Update value items
        if "items" in values_data:
            models.AboutValue.objects.all().delete()
            for idx, value in enumerate(values_data["items"]):
                models.AboutValue.objects.create(
                    key=value.get("id", f"value_{idx}"),
                    icon=value["icon"],
                    title=value["title"],
                    description=value["description"],
                    sort_order=idx + 1
                )
    
    # Update Community
    if "community" in data:
        community = models.AboutCommunity.get_solo()
        community_data = data["community"]
        for field in ["eyebrow", "heading", "description", "image_alt"]:
            if field in community_data:
                setattr(community, field, community_data[field])
        community.save()
        
        # Update bullets
        if "bullets" in community_data:
            models.AboutCommunityBullet.objects.all().delete()
            for idx, bullet_text in enumerate(community_data["bullets"]):
                models.AboutCommunityBullet.objects.create(
                    text=bullet_text,
                    sort_order=idx + 1
                )
    
    # Update Team Section
    if "team" in data:
        team = models.AboutTeam.get_solo()
        team_data = data["team"]
        for field in ["eyebrow", "heading", "description"]:
            if field in team_data:
                setattr(team, field, team_data[field])
        team.save()
        
        # Update members
        if "members" in team_data:
            models.AboutTeamMember.objects.all().delete()
            for idx, member in enumerate(team_data["members"]):
                models.AboutTeamMember.objects.create(
                    key=member.get("id", f"member_{idx}"),
                    full_name=member["full_name"],
                    role=member["role"],
                    sort_order=idx + 1
                )
    
    # Update CTA
    if "cta_banner" in data:
        cta = models.AboutCTA.get_solo()
        cta_data = data["cta_banner"]
        for field in ["heading", "description",
                      "primary_cta_label", "primary_cta_href", "primary_cta_style",
                      "secondary_cta_label", "secondary_cta_href", "secondary_cta_style"]:
            if field in cta_data:
                setattr(cta, field, cta_data[field])
        cta.save()
    
    invalidate_about_page_cache()
    
    from cms.selectors import get_about_page_data
    return get_about_page_data()


@transaction.atomic
def update_contact_page_content(data: dict[str, Any]) -> dict[str, Any]:
    """Update contact page content from provided data."""
    # Update Meta
    if "meta_title" in data or "meta_description" in data:
        meta = models.ContactPageMeta.get_solo()
        if "meta_title" in data:
            meta.meta_title = data["meta_title"]
        if "meta_description" in data:
            meta.meta_description = data["meta_description"]
        meta.save()
    
    # Update Header
    if "header" in data:
        header = models.ContactHeader.get_solo()
        header_data = data["header"]
        for field in ["eyebrow", "title", "description"]:
            if field in header_data:
                setattr(header, field, header_data[field])
        header.save()
    
    # Update Form
    if "form" in data:
        form = models.ContactForm.get_solo()
        form_data = data["form"]
        
        # Simple fields
        for field in ["heading", "description", "submit_label", "submitting_label", "again_label"]:
            if field in form_data:
                setattr(form, field, form_data[field])
        
        # Success message
        if "success" in form_data:
            if "title" in form_data["success"]:
                form.success_title = form_data["success"]["title"]
            if "description" in form_data["success"]:
                form.success_description = form_data["success"]["description"]
        
        # Form fields
        if "fields" in form_data:
            fields = form_data["fields"]
            if "name" in fields:
                form.name_label = fields["name"].get("label", form.name_label)
                form.name_placeholder = fields["name"].get("placeholder", form.name_placeholder)
            if "email" in fields:
                form.email_label = fields["email"].get("label", form.email_label)
                form.email_placeholder = fields["email"].get("placeholder", form.email_placeholder)
            if "phone_number" in fields:
                form.phone_label = fields["phone_number"].get("label", form.phone_label)
                form.phone_placeholder = fields["phone_number"].get("placeholder", form.phone_placeholder)
            if "subject" in fields:
                form.subject_label = fields["subject"].get("label", form.subject_label)
                form.subject_placeholder = fields["subject"].get("placeholder", form.subject_placeholder)
            if "message" in fields:
                form.message_label = fields["message"].get("label", form.message_label)
                form.message_placeholder = fields["message"].get("placeholder", form.message_placeholder)
        
        form.save()
    
    # Update Details Section
    if "details" in data:
        details = models.ContactDetails.get_solo()
        details_data = data["details"]
        for field in ["heading", "description", "maps_label"]:
            if field in details_data:
                setattr(details, field, details_data[field])
        details.save()
        
        # Update detail items
        if "items" in details_data:
            models.ContactDetailItem.objects.all().delete()
            for idx, item in enumerate(details_data["items"]):
                models.ContactDetailItem.objects.create(
                    key=item.get("id", f"item_{idx}"),
                    item_type=item["type"],
                    label=item["label"],
                    hint=item.get("hint", ""),
                    value_source=item.get("value_source", ""),
                    sort_order=idx + 1
                )
    
    # Update Booking Card
    if "booking_card" in data:
        card = models.ContactBookingCard.get_solo()
        card_data = data["booking_card"]
        for field in ["title", "description"]:
            if field in card_data:
                setattr(card, field, card_data[field])
        
        if "cta" in card_data:
            card.cta_label = card_data["cta"].get("label", card.cta_label)
            card.cta_href = card_data["cta"].get("href", card.cta_href)
            card.cta_style = card_data["cta"].get("style", card.cta_style)
        
        card.save()
    
    invalidate_contact_page_cache()
    
    from cms.selectors import get_contact_page_data
    return get_contact_page_data()
