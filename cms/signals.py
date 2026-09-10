"""CMS signals for cache invalidation."""
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from cms import models
from cms.selectors import (
    invalidate_about_page_cache,
    invalidate_bookings_page_cache,
    invalidate_contact_page_cache,
    invalidate_gallery_page_cache,
    invalidate_homepage_cache,
)


# List of all CMS models that affect the homepage
HOMEPAGE_MODELS = [
    models.HomepageMeta,
    models.HeroSection,
    models.StatItem,
    models.ArenaSection,
    models.ArenaHighlight,
    models.ArenaImage,
    models.FeaturesSection,
    models.FeatureItem,
    models.HowItWorksSection,
    models.HowItWorksStep,
    models.GalleryPreviewSection,
    models.GalleryPreviewPhoto,
    models.TestimonialsSection,
    models.Testimonial,
    models.CTABannerSection,
]

# List of all CMS models that affect the bookings page
BOOKINGS_PAGE_MODELS = [
    models.BookingsPageMeta,
    models.BookingsBanner,
    models.BookingsStepsSection,
    models.BookingsStep,
    models.BookingsRatesSection,
    models.BookingsRateRow,
    models.BookingsPoliciesSection,
    models.BookingsPolicy,
    models.BookingsHelpStrip,
]

# List of all CMS models that affect the gallery page
GALLERY_PAGE_MODELS = [
    models.GalleryPageMeta,
    models.GalleryHeader,
    models.GalleryCategory,
    models.GalleryPhoto,
    models.GalleryVideosSection,
    models.GalleryVideo,
    models.GalleryCTA,
]

# List of all CMS models that affect the about page
ABOUT_PAGE_MODELS = [
    models.AboutPageMeta,
    models.AboutHero,
    models.AboutStat,
    models.AboutStory,
    models.AboutMilestone,
    models.AboutValues,
    models.AboutValue,
    models.AboutCommunity,
    models.AboutCommunityBullet,
    models.AboutTeam,
    models.AboutTeamMember,
    models.AboutCTA,
]

# List of all CMS models that affect the contact page
CONTACT_PAGE_MODELS = [
    models.ContactPageMeta,
    models.ContactHeader,
    models.ContactForm,
    models.ContactDetails,
    models.ContactDetailItem,
    models.ContactBookingCard,
]


@receiver(post_save)
def invalidate_cache_on_save(sender, instance, **kwargs):
    """Invalidate page caches when any CMS model is saved."""
    if sender in HOMEPAGE_MODELS:
        invalidate_homepage_cache()
    if sender in BOOKINGS_PAGE_MODELS:
        invalidate_bookings_page_cache()
    if sender in GALLERY_PAGE_MODELS:
        invalidate_gallery_page_cache()
    if sender in ABOUT_PAGE_MODELS:
        invalidate_about_page_cache()
    if sender in CONTACT_PAGE_MODELS:
        invalidate_contact_page_cache()


@receiver(post_delete)
def invalidate_cache_on_delete(sender, instance, **kwargs):
    """Invalidate page caches when any CMS model is deleted."""
    if sender in HOMEPAGE_MODELS:
        invalidate_homepage_cache()
    if sender in BOOKINGS_PAGE_MODELS:
        invalidate_bookings_page_cache()
    if sender in GALLERY_PAGE_MODELS:
        invalidate_gallery_page_cache()
    if sender in ABOUT_PAGE_MODELS:
        invalidate_about_page_cache()
    if sender in CONTACT_PAGE_MODELS:
        invalidate_contact_page_cache()
