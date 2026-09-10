"""CMS data selectors for assembling homepage content."""
from __future__ import annotations

from django.core.cache import cache

from cms import models


def get_homepage_data() -> dict:
    """
    Assemble complete homepage data from CMS models.
    
    Returns a structured dictionary matching the homepage API contract,
    with all sections in render order.
    """
    # Try to get from cache first
    cache_key = "cms:homepage:data"
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    # Get singleton sections
    meta = models.HomepageMeta.get_solo()
    hero = models.HeroSection.get_solo()
    arena_section = models.ArenaSection.get_solo()
    features_section = models.FeaturesSection.get_solo()
    how_it_works_section = models.HowItWorksSection.get_solo()
    gallery_section = models.GalleryPreviewSection.get_solo()
    testimonials_section = models.TestimonialsSection.get_solo()
    cta_banner = models.CTABannerSection.get_solo()
    
    # Get list items
    stats = list(models.StatItem.objects.filter(is_active=True))
    arena_highlights = list(models.ArenaHighlight.objects.filter(is_active=True))
    arena_images = list(models.ArenaImage.objects.filter(is_active=True))
    features = list(models.FeatureItem.objects.filter(is_active=True))
    how_it_works_steps = list(models.HowItWorksStep.objects.filter(is_active=True))
    gallery_photos = list(models.GalleryPreviewPhoto.objects.filter(is_active=True))
    testimonials = list(models.Testimonial.objects.filter(is_active=True))
    
    # Determine the latest update time from all relevant models
    latest_update = max(
        meta.updated_at,
        hero.updated_at,
        arena_section.updated_at,
        features_section.updated_at,
        how_it_works_section.updated_at,
        gallery_section.updated_at,
        testimonials_section.updated_at,
        cta_banner.updated_at,
        max((item.updated_at for item in stats), default=meta.updated_at),
        max((item.updated_at for item in arena_highlights), default=meta.updated_at),
        max((item.updated_at for item in arena_images), default=meta.updated_at),
        max((item.updated_at for item in features), default=meta.updated_at),
        max((item.updated_at for item in how_it_works_steps), default=meta.updated_at),
        max((item.updated_at for item in gallery_photos), default=meta.updated_at),
        max((item.updated_at for item in testimonials), default=meta.updated_at),
    )
    
    # Assemble the complete data structure
    data = {
        "meta_title": meta.meta_title,
        "meta_description": meta.meta_description,
        "updated_at": latest_update,
        
        "hero": {
            "badge": hero.badge,
            "title": hero.title,
            "title_highlight": hero.title_highlight or None,
            "description": hero.description,
            "image": {
                "url": hero.image.url if hero.image else "",
                "alt": hero.image_alt,
            },
            "primary_cta": {
                "label": hero.primary_cta_label,
                "href": hero.primary_cta_href,
                "style": hero.primary_cta_style,
            },
            "secondary_cta": {
                "label": hero.secondary_cta_label,
                "href": hero.secondary_cta_href,
                "style": hero.secondary_cta_style,
            },
        },
        
        "stats": [
            {
                "key": stat.key,
                "value": stat.value,
                "label": stat.label,
            }
            for stat in stats
        ],
        
        "arena": {
            "eyebrow": arena_section.eyebrow,
            "heading": arena_section.heading,
            "description": arena_section.description,
            "since_label": arena_section.since_label,
            "highlights": [
                {
                    "key": highlight.key,
                    "icon": highlight.icon,
                    "text": highlight.text,
                }
                for highlight in arena_highlights
            ],
            "images": [
                {
                    "key": image.key,
                    "url": image.image.url if image.image else "",
                    "alt_text": image.alt_text,
                }
                for image in arena_images
            ],
        },
        
        "features": {
            "eyebrow": features_section.eyebrow,
            "heading": features_section.heading,
            "items": [
                {
                    "key": feature.key,
                    "icon": feature.icon,
                    "title": feature.title,
                    "description": feature.description,
                }
                for feature in features
            ],
        },
        
        "how_it_works": {
            "eyebrow": how_it_works_section.eyebrow,
            "heading": how_it_works_section.heading,
            "steps": [
                {
                    "key": step.key,
                    "icon": step.icon,
                    "title": step.title,
                    "description": step.description,
                }
                for step in how_it_works_steps
            ],
        },
        
        "gallery_preview": {
            "eyebrow": gallery_section.eyebrow,
            "heading": gallery_section.heading,
            "description": gallery_section.description,
            "count_label": gallery_section.count_label,
            "cta": {
                "label": gallery_section.cta_label,
                "href": gallery_section.cta_href,
                "style": gallery_section.cta_style,
            },
            "photos": [
                {
                    "key": photo.key,
                    "url": photo.image.url if photo.image else "",
                    "alt_text": photo.alt_text,
                    "aspect_ratio": photo.aspect_ratio,
                }
                for photo in gallery_photos
            ],
        },
        
        "testimonials": {
            "eyebrow": testimonials_section.eyebrow,
            "heading": testimonials_section.heading,
            "items": [
                {
                    "key": testimonial.key,
                    "quote": testimonial.quote,
                    "name": testimonial.name,
                    "role": testimonial.role,
                    "avatar": testimonial.avatar.url if testimonial.avatar else None,
                }
                for testimonial in testimonials
            ],
        },
        
        "cta_banner": {
            "heading": cta_banner.heading,
            "description": cta_banner.description,
            "primary_cta": {
                "label": cta_banner.primary_cta_label,
                "href": cta_banner.primary_cta_href,
                "style": cta_banner.primary_cta_style,
            },
            "secondary_cta": {
                "label": cta_banner.secondary_cta_label,
                "href": cta_banner.secondary_cta_href,
                "style": cta_banner.secondary_cta_style,
            },
        },
    }
    
    # Cache for 5 minutes (can be adjusted)
    cache.set(cache_key, data, timeout=300)
    
    return data


def invalidate_homepage_cache() -> None:
    """Invalidate the homepage cache when content is updated."""
    cache.delete("cms:homepage:data")



def get_bookings_page_data() -> dict:
    """
    Assemble complete bookings page data from CMS models.
    
    Returns a structured dictionary matching the bookings page API contract.
    """
    # Try to get from cache first
    cache_key = "cms:bookings:data"
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    # Get singleton sections
    meta = models.BookingsPageMeta.get_solo()
    banner = models.BookingsBanner.get_solo()
    steps_section = models.BookingsStepsSection.get_solo()
    rates_section = models.BookingsRatesSection.get_solo()
    policies_section = models.BookingsPoliciesSection.get_solo()
    help_strip = models.BookingsHelpStrip.get_solo()
    
    # Get list items
    steps = list(models.BookingsStep.objects.filter(is_active=True))
    rate_rows = list(models.BookingsRateRow.objects.filter(is_active=True))
    policies = list(models.BookingsPolicy.objects.filter(is_active=True))
    
    # Determine the latest update time
    latest_update = max(
        meta.updated_at,
        banner.updated_at,
        steps_section.updated_at,
        rates_section.updated_at,
        policies_section.updated_at,
        help_strip.updated_at,
        max((item.updated_at for item in steps), default=meta.updated_at),
        max((item.updated_at for item in rate_rows), default=meta.updated_at),
        max((item.updated_at for item in policies), default=meta.updated_at),
    )
    
    # Assemble the complete data structure
    data = {
        "meta_title": meta.meta_title,
        "meta_description": meta.meta_description,
        "updated_at": latest_update,
        
        "banner": {
            "eyebrow": banner.eyebrow,
            "title": banner.title,
            "description": banner.description,
            "image": {
                "url": banner.image.url if banner.image else "",
                "alt": banner.image_alt,
            },
        },
        
        "steps": {
            "heading": steps_section.heading,
            "items": [
                {
                    "key": step.key,
                    "title": step.title,
                    "description": step.description,
                }
                for step in steps
            ],
        },
        
        "rates": {
            "heading": rates_section.heading,
            "description": rates_section.description,
            "weekday_label": rates_section.weekday_label,
            "weekend_label": rates_section.weekend_label,
            "rows": [
                {
                    "key": row.key,
                    "title": row.title,
                    "hours": row.hours,
                    "weekday_price": row.weekday_price,
                    "weekend_price": row.weekend_price,
                    "highlight": row.highlight,
                    "highlight_label": row.highlight_label,
                }
                for row in rate_rows
            ],
            "events": {
                "title": rates_section.events_title,
                "description": rates_section.events_description,
                "cta": {
                    "label": rates_section.events_cta_label,
                    "href": rates_section.events_cta_href,
                    "style": rates_section.events_cta_style,
                },
            },
            "refreshments_note": rates_section.refreshments_note,
        },
        
        "policies": {
            "heading": policies_section.heading,
            "items": [
                {
                    "key": policy.key,
                    "icon": policy.icon,
                    "title": policy.title,
                    "description": policy.description,
                }
                for policy in policies
            ],
        },
        
        "help_strip": {
            "heading": help_strip.heading,
            "description": help_strip.description,
            "cta": {
                "label": help_strip.cta_label,
                "href": help_strip.cta_href,
                "style": help_strip.cta_style,
            },
        },
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, data, timeout=300)
    
    return data


def invalidate_bookings_page_cache() -> None:
    """Invalidate the bookings page cache when content is updated."""
    cache.delete("cms:bookings:data")



def get_gallery_page_data() -> dict:
    """
    Assemble complete gallery page data from CMS models.
    
    Returns a structured dictionary matching the gallery page API contract.
    """
    # Try to get from cache first
    cache_key = "cms:gallery:data"
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    # Get singleton sections
    meta = models.GalleryPageMeta.get_solo()
    header = models.GalleryHeader.get_solo()
    videos_section = models.GalleryVideosSection.get_solo()
    cta = models.GalleryCTA.get_solo()
    
    # Get list items
    categories = list(models.GalleryCategory.objects.filter(is_active=True))
    photos = list(models.GalleryPhoto.objects.filter(is_active=True))
    videos = list(models.GalleryVideo.objects.filter(is_active=True))
    
    # Determine the latest update time
    latest_update = max(
        meta.updated_at,
        header.updated_at,
        videos_section.updated_at,
        cta.updated_at,
        max((item.updated_at for item in categories), default=meta.updated_at),
        max((item.updated_at for item in photos), default=meta.updated_at),
        max((item.updated_at for item in videos), default=meta.updated_at),
    )
    
    # Assemble the complete data structure
    data = {
        "meta_title": meta.meta_title,
        "meta_description": meta.meta_description,
        "updated_at": latest_update,
        
        "header": {
            "eyebrow": header.eyebrow,
            "title": header.title,
            "description": header.description,
        },
        
        "categories": [
            {
                "key": category.key,
                "label": category.label,
            }
            for category in categories
        ],
        
        "photos": [
            {
                "key": photo.key,
                "url": photo.image.url if photo.image else "",
                "alt_text": photo.alt_text,
                "title": photo.title,
                "category": photo.category,
                "aspect_ratio": photo.aspect_ratio,
            }
            for photo in photos
        ],
        
        "videos_section": {
            "heading": videos_section.heading,
            "description": videos_section.description,
            "videos": [
                {
                    "key": video.key,
                    "url": video.video.url if video.video else "",
                    "poster": video.poster.url if video.poster else "",
                    "title": video.title,
                    "category": video.category,
                    "duration_seconds": video.duration_seconds,
                }
                for video in videos
            ],
        },
        
        "cta": {
            "heading": cta.heading,
            "description": cta.description,
            "button": {
                "label": cta.button_label,
                "href": cta.button_href,
                "style": cta.button_style,
            },
        },
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, data, timeout=300)
    
    return data


def invalidate_gallery_page_cache() -> None:
    """Invalidate the gallery page cache when content is updated."""
    cache.delete("cms:gallery:data")



def get_about_page_data() -> dict:
    """
    Assemble complete about page data from CMS models.
    
    Returns a structured dictionary matching the about page API contract,
    with all sections in render order: Hero → Stats → Story → Values → Community → Team → CTA.
    """
    # Try to get from cache first
    cache_key = "cms:about:data"
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    # Get singleton sections
    meta = models.AboutPageMeta.get_solo()
    hero = models.AboutHero.get_solo()
    story = models.AboutStory.get_solo()
    values_section = models.AboutValues.get_solo()
    community = models.AboutCommunity.get_solo()
    team_section = models.AboutTeam.get_solo()
    cta = models.AboutCTA.get_solo()
    
    # Get list items
    stats = list(models.AboutStat.objects.filter(is_active=True))
    milestones = list(models.AboutMilestone.objects.filter(is_active=True))
    values = list(models.AboutValue.objects.filter(is_active=True))
    community_bullets = list(models.AboutCommunityBullet.objects.filter(is_active=True))
    team_members = list(models.AboutTeamMember.objects.filter(is_active=True))
    
    # Determine the latest update time
    latest_update = max(
        meta.updated_at,
        hero.updated_at,
        story.updated_at,
        values_section.updated_at,
        community.updated_at,
        team_section.updated_at,
        cta.updated_at,
        max((item.updated_at for item in stats), default=meta.updated_at),
        max((item.updated_at for item in milestones), default=meta.updated_at),
        max((item.updated_at for item in values), default=meta.updated_at),
        max((item.updated_at for item in community_bullets), default=meta.updated_at),
        max((item.updated_at for item in team_members), default=meta.updated_at),
    )
    
    # Assemble the complete data structure
    data = {
        "meta_title": meta.meta_title,
        "meta_description": meta.meta_description,
        "updated_at": latest_update,
        
        "hero": {
            "eyebrow": hero.eyebrow,
            "title": hero.title,
            "title_highlight": hero.title_highlight,
            "description": hero.description,
            "image": {
                "url": hero.image.url if hero.image else "",
                "alt": hero.image_alt,
            },
        },
        
        "stats": [
            {
                "key": stat.key,
                "value": stat.value,
                "label": stat.label,
            }
            for stat in stats
        ],
        
        "story": {
            "eyebrow": story.eyebrow,
            "heading": story.heading,
            "description": story.description,
            "timeline_heading": story.timeline_heading,
            "timeline_hint": story.timeline_hint,
            "milestones": [
                {
                    "key": milestone.key,
                    "year": milestone.year,
                    "title": milestone.title,
                    "description": milestone.description,
                    "image": {
                        "url": milestone.image.url if milestone.image else "",
                        "alt": milestone.image_alt,
                    },
                }
                for milestone in milestones
            ],
        },
        
        "values": {
            "eyebrow": values_section.eyebrow,
            "heading": values_section.heading,
            "items": [
                {
                    "key": value.key,
                    "icon": value.icon,
                    "title": value.title,
                    "description": value.description,
                }
                for value in values
            ],
        },
        
        "community": {
            "eyebrow": community.eyebrow,
            "heading": community.heading,
            "description": community.description,
            "bullets": [bullet.text for bullet in community_bullets],
            "image": {
                "url": community.image.url if community.image else "",
                "alt": community.image_alt,
            },
        },
        
        "team": {
            "eyebrow": team_section.eyebrow,
            "heading": team_section.heading,
            "description": team_section.description,
            "members": [
                {
                    "key": member.key,
                    "full_name": member.full_name,
                    "role": member.role,
                    "profile_image": member.profile_image.url if member.profile_image else None,
                }
                for member in team_members
            ],
        },
        
        "cta_banner": {
            "heading": cta.heading,
            "description": cta.description,
            "primary_cta": {
                "label": cta.primary_cta_label,
                "href": cta.primary_cta_href,
                "style": cta.primary_cta_style,
            },
            "secondary_cta": {
                "label": cta.secondary_cta_label,
                "href": cta.secondary_cta_href,
                "style": cta.secondary_cta_style,
            },
        },
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, data, timeout=300)
    
    return data


def invalidate_about_page_cache() -> None:
    """Invalidate the about page cache when content is updated."""
    cache.delete("cms:about:data")



def get_contact_page_data() -> dict:
    """
    Assemble complete contact page data from CMS models.
    
    Returns a structured dictionary matching the contact page API contract.
    Form field labels/placeholders and contact detail presentation copy only.
    Actual contact values (address, phone, email, hours) come from /api/v1/futsal/.
    """
    # Try to get from cache first
    cache_key = "cms:contact:data"
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    # Get singleton sections
    meta = models.ContactPageMeta.get_solo()
    header = models.ContactHeader.get_solo()
    form = models.ContactForm.get_solo()
    details_section = models.ContactDetails.get_solo()
    booking_card = models.ContactBookingCard.get_solo()
    
    # Get list items
    detail_items = list(models.ContactDetailItem.objects.filter(is_active=True))
    
    # Determine the latest update time
    latest_update = max(
        meta.updated_at,
        header.updated_at,
        form.updated_at,
        details_section.updated_at,
        booking_card.updated_at,
        max((item.updated_at for item in detail_items), default=meta.updated_at),
    )
    
    # Assemble the complete data structure
    data = {
        "meta_title": meta.meta_title,
        "meta_description": meta.meta_description,
        "updated_at": latest_update,
        
        "header": {
            "eyebrow": header.eyebrow,
            "title": header.title,
            "description": header.description,
        },
        
        "form": {
            "heading": form.heading,
            "description": form.description,
            "submit_label": form.submit_label,
            "submitting_label": form.submitting_label,
            "fields": {
                "name": {
                    "label": form.name_label,
                    "placeholder": form.name_placeholder,
                },
                "email": {
                    "label": form.email_label,
                    "placeholder": form.email_placeholder,
                },
                "phone_number": {
                    "label": form.phone_label,
                    "placeholder": form.phone_placeholder,
                },
                "subject": {
                    "label": form.subject_label,
                    "placeholder": form.subject_placeholder,
                },
                "message": {
                    "label": form.message_label,
                    "placeholder": form.message_placeholder,
                },
            },
            "success": {
                "title": form.success_title,
                "description": form.success_description,
            },
            "again_label": form.again_label,
        },
        
        "details": {
            "heading": details_section.heading,
            "description": details_section.description,
            "maps_label": details_section.maps_label,
            "items": [
                {
                    "key": item.key,
                    "item_type": item.item_type,
                    "label": item.label,
                    "hint": item.hint or None,
                    "value_source": item.value_source,
                }
                for item in detail_items
            ],
        },
        
        "booking_card": {
            "title": booking_card.title,
            "description": booking_card.description,
            "cta": {
                "label": booking_card.cta_label,
                "href": booking_card.cta_href,
                "style": booking_card.cta_style,
            },
        },
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, data, timeout=300)
    
    return data


def invalidate_contact_page_cache() -> None:
    """Invalidate the contact page cache when content is updated."""
    cache.delete("cms:contact:data")
