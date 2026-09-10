"""CMS admin interface."""
from django.contrib import admin

from cms import models


@admin.register(models.HomepageMeta)
class HomepageMetaAdmin(admin.ModelAdmin):
    """Admin for homepage SEO metadata."""
    
    list_display = ["meta_title", "updated_at"]
    fieldsets = [
        ("SEO Metadata", {
            "fields": ["meta_title", "meta_description"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not models.HomepageMeta.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of the singleton
        return False


@admin.register(models.HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    """Admin for hero section."""
    
    list_display = ["title", "badge", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["badge", "title", "title_highlight", "description"],
        }),
        ("Image", {
            "fields": ["image", "image_alt"],
        }),
        ("Primary CTA", {
            "fields": ["primary_cta_label", "primary_cta_href", "primary_cta_style"],
        }),
        ("Secondary CTA", {
            "fields": ["secondary_cta_label", "secondary_cta_href", "secondary_cta_style"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.HeroSection.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.StatItem)
class StatItemAdmin(admin.ModelAdmin):
    """Admin for stat items."""
    
    list_display = ["key", "value", "label", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "label", "value"]
    ordering = ["sort_order", "created_at"]


@admin.register(models.ArenaSection)
class ArenaSectionAdmin(admin.ModelAdmin):
    """Admin for arena section."""
    
    list_display = ["heading", "eyebrow", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["eyebrow", "heading", "description", "since_label"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.ArenaSection.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.ArenaHighlight)
class ArenaHighlightAdmin(admin.ModelAdmin):
    """Admin for arena highlights."""
    
    list_display = ["key", "text", "icon", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "text"]
    ordering = ["sort_order", "created_at"]


@admin.register(models.ArenaImage)
class ArenaImageAdmin(admin.ModelAdmin):
    """Admin for arena images."""
    
    list_display = ["key", "alt_text", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "alt_text"]
    ordering = ["sort_order", "created_at"]


@admin.register(models.FeaturesSection)
class FeaturesSectionAdmin(admin.ModelAdmin):
    """Admin for features section."""
    
    list_display = ["heading", "eyebrow", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["eyebrow", "heading"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.FeaturesSection.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.FeatureItem)
class FeatureItemAdmin(admin.ModelAdmin):
    """Admin for feature items."""
    
    list_display = ["key", "title", "icon", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "title", "description"]
    ordering = ["sort_order", "created_at"]


@admin.register(models.HowItWorksSection)
class HowItWorksSectionAdmin(admin.ModelAdmin):
    """Admin for how it works section."""
    
    list_display = ["heading", "eyebrow", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["eyebrow", "heading"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.HowItWorksSection.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.HowItWorksStep)
class HowItWorksStepAdmin(admin.ModelAdmin):
    """Admin for how it works steps."""
    
    list_display = ["key", "title", "icon", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "title", "description"]
    ordering = ["sort_order", "created_at"]


@admin.register(models.GalleryPreviewSection)
class GalleryPreviewSectionAdmin(admin.ModelAdmin):
    """Admin for gallery preview section."""
    
    list_display = ["heading", "eyebrow", "count_label", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["eyebrow", "heading", "description", "count_label"],
        }),
        ("CTA", {
            "fields": ["cta_label", "cta_href", "cta_style"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.GalleryPreviewSection.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.GalleryPreviewPhoto)
class GalleryPreviewPhotoAdmin(admin.ModelAdmin):
    """Admin for gallery preview photos."""
    
    list_display = ["key", "alt_text", "aspect_ratio", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active", "aspect_ratio"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "alt_text"]
    ordering = ["sort_order", "created_at"]


@admin.register(models.TestimonialsSection)
class TestimonialsSectionAdmin(admin.ModelAdmin):
    """Admin for testimonials section."""
    
    list_display = ["heading", "eyebrow", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["eyebrow", "heading"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.TestimonialsSection.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """Admin for testimonials."""
    
    list_display = ["key", "name", "role", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "name", "role", "quote"]
    ordering = ["sort_order", "created_at"]
    fieldsets = [
        ("Content", {
            "fields": ["key", "quote", "name", "role", "avatar"],
        }),
        ("Display", {
            "fields": ["sort_order", "is_active"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(models.CTABannerSection)
class CTABannerSectionAdmin(admin.ModelAdmin):
    """Admin for CTA banner section."""
    
    list_display = ["heading", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["heading", "description"],
        }),
        ("Primary CTA", {
            "fields": ["primary_cta_label", "primary_cta_href", "primary_cta_style"],
        }),
        ("Secondary CTA", {
            "fields": ["secondary_cta_label", "secondary_cta_href", "secondary_cta_style"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.CTABannerSection.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False



# ============================================================================
# Bookings Page Admin
# ============================================================================


@admin.register(models.BookingsPageMeta)
class BookingsPageMetaAdmin(admin.ModelAdmin):
    """Admin for bookings page SEO metadata."""
    
    list_display = ["meta_title", "updated_at"]
    fieldsets = [
        ("SEO Metadata", {
            "fields": ["meta_title", "meta_description"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.BookingsPageMeta.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.BookingsBanner)
class BookingsBannerAdmin(admin.ModelAdmin):
    """Admin for bookings banner."""
    
    list_display = ["title", "eyebrow", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["eyebrow", "title", "description"],
        }),
        ("Image", {
            "fields": ["image", "image_alt"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.BookingsBanner.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.BookingsStepsSection)
class BookingsStepsSectionAdmin(admin.ModelAdmin):
    """Admin for bookings steps section."""
    
    list_display = ["heading", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["heading"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.BookingsStepsSection.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.BookingsStep)
class BookingsStepAdmin(admin.ModelAdmin):
    """Admin for bookings steps."""
    
    list_display = ["key", "title", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "title", "description"]
    ordering = ["sort_order", "created_at"]


@admin.register(models.BookingsRatesSection)
class BookingsRatesSectionAdmin(admin.ModelAdmin):
    """Admin for bookings rates section."""
    
    list_display = ["heading", "updated_at"]
    fieldsets = [
        ("Section Header", {
            "fields": ["heading", "description", "weekday_label", "weekend_label"],
        }),
        ("Events Subsection", {
            "fields": ["events_title", "events_description", "events_cta_label", 
                      "events_cta_href", "events_cta_style"],
        }),
        ("Footer Note", {
            "fields": ["refreshments_note"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.BookingsRatesSection.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.BookingsRateRow)
class BookingsRateRowAdmin(admin.ModelAdmin):
    """Admin for rate rows."""
    
    list_display = ["key", "title", "hours", "weekday_price", "weekend_price", 
                   "highlight", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active", "highlight"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "title", "hours"]
    ordering = ["sort_order", "created_at"]
    fieldsets = [
        ("Content", {
            "fields": ["key", "title", "hours"],
        }),
        ("Pricing", {
            "fields": ["weekday_price", "weekend_price"],
        }),
        ("Highlight", {
            "fields": ["highlight", "highlight_label"],
        }),
        ("Display", {
            "fields": ["sort_order", "is_active"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(models.BookingsPoliciesSection)
class BookingsPoliciesSectionAdmin(admin.ModelAdmin):
    """Admin for bookings policies section."""
    
    list_display = ["heading", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["heading"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.BookingsPoliciesSection.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.BookingsPolicy)
class BookingsPolicyAdmin(admin.ModelAdmin):
    """Admin for bookings policies."""
    
    list_display = ["key", "title", "icon", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "title", "description"]
    ordering = ["sort_order", "created_at"]


@admin.register(models.BookingsHelpStrip)
class BookingsHelpStripAdmin(admin.ModelAdmin):
    """Admin for bookings help strip."""
    
    list_display = ["heading", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["heading", "description"],
        }),
        ("CTA", {
            "fields": ["cta_label", "cta_href", "cta_style"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.BookingsHelpStrip.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False



# ============================================================================
# Gallery Page Admin
# ============================================================================


@admin.register(models.GalleryPageMeta)
class GalleryPageMetaAdmin(admin.ModelAdmin):
    """Admin for gallery page SEO metadata."""
    
    list_display = ["meta_title", "updated_at"]
    fieldsets = [
        ("SEO Metadata", {
            "fields": ["meta_title", "meta_description"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.GalleryPageMeta.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.GalleryHeader)
class GalleryHeaderAdmin(admin.ModelAdmin):
    """Admin for gallery header."""
    
    list_display = ["title", "eyebrow", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["eyebrow", "title", "description"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.GalleryHeader.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    """Admin for gallery categories."""
    
    list_display = ["key", "label", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "label"]
    ordering = ["sort_order", "created_at"]
    
    fieldsets = [
        ("Content", {
            "fields": ["key", "label"],
            "description": "Key should be UPPERCASE (e.g., 'ALL', 'VENUE', 'MATCHES')",
        }),
        ("Display", {
            "fields": ["sort_order", "is_active"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(models.GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    """Admin for gallery photos."""
    
    list_display = ["key", "title", "category", "aspect_ratio", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active", "category", "aspect_ratio"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "title", "alt_text", "category"]
    ordering = ["sort_order", "created_at"]
    
    fieldsets = [
        ("Image", {
            "fields": ["key", "image"],
        }),
        ("Content", {
            "fields": ["title", "alt_text", "category", "aspect_ratio"],
        }),
        ("Display", {
            "fields": ["sort_order", "is_active"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(models.GalleryVideosSection)
class GalleryVideosSectionAdmin(admin.ModelAdmin):
    """Admin for gallery videos section."""
    
    list_display = ["heading", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["heading", "description"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.GalleryVideosSection.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.GalleryVideo)
class GalleryVideoAdmin(admin.ModelAdmin):
    """Admin for gallery videos."""
    
    list_display = ["key", "title", "category", "duration_seconds", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active", "category"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "title", "category"]
    ordering = ["sort_order", "created_at"]
    
    fieldsets = [
        ("Video", {
            "fields": ["key", "video", "poster"],
        }),
        ("Content", {
            "fields": ["title", "category", "duration_seconds"],
        }),
        ("Display", {
            "fields": ["sort_order", "is_active"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(models.GalleryCTA)
class GalleryCTAAdmin(admin.ModelAdmin):
    """Admin for gallery CTA."""
    
    list_display = ["heading", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["heading", "description"],
        }),
        ("Button", {
            "fields": ["button_label", "button_href", "button_style"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.GalleryCTA.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False



# ============================================================================
# About Page Admin
# ============================================================================


@admin.register(models.AboutPageMeta)
class AboutPageMetaAdmin(admin.ModelAdmin):
    """Admin for about page SEO metadata."""
    
    list_display = ["meta_title", "updated_at"]
    fieldsets = [
        ("SEO Metadata", {
            "fields": ["meta_title", "meta_description"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.AboutPageMeta.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.AboutHero)
class AboutHeroAdmin(admin.ModelAdmin):
    """Admin for about hero section."""
    
    list_display = ["eyebrow", "title", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["eyebrow", "title", "title_highlight", "description"],
        }),
        ("Image", {
            "fields": ["image", "image_alt"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.AboutHero.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.AboutStat)
class AboutStatAdmin(admin.ModelAdmin):
    """Admin for about stats."""
    
    list_display = ["key", "value", "label", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "value", "label"]
    ordering = ["sort_order", "created_at"]
    
    fieldsets = [
        ("Content", {
            "fields": ["key", "value", "label"],
            "description": "E.g., key='years', value='8+', label='Years in the game'",
        }),
        ("Display", {
            "fields": ["sort_order", "is_active"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(models.AboutStory)
class AboutStoryAdmin(admin.ModelAdmin):
    """Admin for about story section."""
    
    list_display = ["heading", "eyebrow", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["eyebrow", "heading", "description"],
        }),
        ("Timeline", {
            "fields": ["timeline_heading", "timeline_hint"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.AboutStory.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.AboutMilestone)
class AboutMilestoneAdmin(admin.ModelAdmin):
    """Admin for about milestones."""
    
    list_display = ["year", "title", "key", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active", "year"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "year", "title", "description"]
    ordering = ["sort_order", "created_at"]
    
    fieldsets = [
        ("Content", {
            "fields": ["key", "year", "title", "description"],
        }),
        ("Image", {
            "fields": ["image", "image_alt"],
        }),
        ("Display", {
            "fields": ["sort_order", "is_active"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(models.AboutValues)
class AboutValuesAdmin(admin.ModelAdmin):
    """Admin for about values section."""
    
    list_display = ["heading", "eyebrow", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["eyebrow", "heading"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.AboutValues.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.AboutValue)
class AboutValueAdmin(admin.ModelAdmin):
    """Admin for about values."""
    
    list_display = ["key", "title", "icon", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "title", "description", "icon"]
    ordering = ["sort_order", "created_at"]
    
    fieldsets = [
        ("Content", {
            "fields": ["key", "icon", "title", "description"],
            "description": "Icon from shared registry (e.g., 'heart-handshake', 'sparkles')",
        }),
        ("Display", {
            "fields": ["sort_order", "is_active"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(models.AboutCommunity)
class AboutCommunityAdmin(admin.ModelAdmin):
    """Admin for about community section."""
    
    list_display = ["heading", "eyebrow", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["eyebrow", "heading", "description"],
        }),
        ("Image", {
            "fields": ["image", "image_alt"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.AboutCommunity.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.AboutCommunityBullet)
class AboutCommunityBulletAdmin(admin.ModelAdmin):
    """Admin for about community bullets."""
    
    list_display = ["text_preview", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["text"]
    ordering = ["sort_order", "created_at"]
    
    def text_preview(self, obj):
        """Show first 100 chars of text."""
        return obj.text[:100] + "..." if len(obj.text) > 100 else obj.text
    text_preview.short_description = "Text"


@admin.register(models.AboutTeam)
class AboutTeamAdmin(admin.ModelAdmin):
    """Admin for about team section."""
    
    list_display = ["heading", "eyebrow", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["eyebrow", "heading", "description"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.AboutTeam.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.AboutTeamMember)
class AboutTeamMemberAdmin(admin.ModelAdmin):
    """Admin for about team members."""
    
    list_display = ["key", "full_name", "role", "has_image", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "full_name", "role"]
    ordering = ["sort_order", "created_at"]
    
    fieldsets = [
        ("Content", {
            "fields": ["key", "full_name", "role"],
        }),
        ("Image", {
            "fields": ["profile_image"],
            "description": "Leave blank to show initials avatar",
        }),
        ("Display", {
            "fields": ["sort_order", "is_active"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_image(self, obj):
        """Show if profile image exists."""
        return bool(obj.profile_image)
    has_image.boolean = True
    has_image.short_description = "Has Image"


@admin.register(models.AboutCTA)
class AboutCTAAdmin(admin.ModelAdmin):
    """Admin for about CTA banner."""
    
    list_display = ["heading", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["heading", "description"],
        }),
        ("Primary CTA", {
            "fields": ["primary_cta_label", "primary_cta_href", "primary_cta_style"],
        }),
        ("Secondary CTA", {
            "fields": ["secondary_cta_label", "secondary_cta_href", "secondary_cta_style"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.AboutCTA.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False



# ============================================================================
# Contact Page Admin
# ============================================================================


@admin.register(models.ContactPageMeta)
class ContactPageMetaAdmin(admin.ModelAdmin):
    """Admin for contact page SEO metadata."""
    
    list_display = ["meta_title", "updated_at"]
    fieldsets = [
        ("SEO Metadata", {
            "fields": ["meta_title", "meta_description"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.ContactPageMeta.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.ContactHeader)
class ContactHeaderAdmin(admin.ModelAdmin):
    """Admin for contact header."""
    
    list_display = ["title", "eyebrow", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["eyebrow", "title", "description"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.ContactHeader.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    """Admin for contact form section."""
    
    list_display = ["heading", "submit_label", "updated_at"]
    fieldsets = [
        ("Form Header", {
            "fields": ["heading", "description"],
        }),
        ("Button Labels", {
            "fields": ["submit_label", "submitting_label", "again_label"],
        }),
        ("Success Message", {
            "fields": ["success_title", "success_description"],
            "description": "Success description supports tokens: {first_name}, {email}",
        }),
        ("Field: Name", {
            "fields": ["name_label", "name_placeholder"],
        }),
        ("Field: Email", {
            "fields": ["email_label", "email_placeholder"],
        }),
        ("Field: Phone", {
            "fields": ["phone_label", "phone_placeholder"],
        }),
        ("Field: Subject", {
            "fields": ["subject_label", "subject_placeholder"],
        }),
        ("Field: Message", {
            "fields": ["message_label", "message_placeholder"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.ContactForm.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.ContactDetails)
class ContactDetailsAdmin(admin.ModelAdmin):
    """Admin for contact details section."""
    
    list_display = ["heading", "maps_label", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["heading", "description", "maps_label"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.ContactDetails.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.ContactDetailItem)
class ContactDetailItemAdmin(admin.ModelAdmin):
    """Admin for contact detail items."""
    
    list_display = ["key", "label", "item_type", "sort_order", "is_active", "updated_at"]
    list_filter = ["is_active", "item_type"]
    list_editable = ["sort_order", "is_active"]
    search_fields = ["key", "label", "value_source"]
    ordering = ["sort_order", "created_at"]
    
    fieldsets = [
        ("Content", {
            "fields": ["key", "item_type", "label", "hint"],
        }),
        ("Value Source", {
            "fields": ["value_source"],
            "description": "Documentation: which futsal field feeds the value (e.g., 'futsal.phone')",
        }),
        ("Display", {
            "fields": ["sort_order", "is_active"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(models.ContactBookingCard)
class ContactBookingCardAdmin(admin.ModelAdmin):
    """Admin for contact booking card."""
    
    list_display = ["title", "cta_label", "updated_at"]
    fieldsets = [
        ("Content", {
            "fields": ["title", "description"],
        }),
        ("CTA", {
            "fields": ["cta_label", "cta_href", "cta_style"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    def has_add_permission(self, request):
        return not models.ContactBookingCard.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
