"""CMS admin configuration."""
from django.contrib import admin
from solo.admin import SingletonModelAdmin

from cms.models import (
    HeroSection,
    CarouselImage,
    Testimonial,
    ArenaSection,
    WhyUsSection,
    GalleryCategory,
    GalleryImage,
    GalleryHighlight,
    AboutHeroSection,
    AboutStory,
    AboutCommunity,
    BookingsHeroSection,
    FAQ,
    TermsAndPrivacy,
)


@admin.register(HeroSection)
class HeroSectionAdmin(SingletonModelAdmin):
    """Admin interface for hero section."""
    
    fieldsets = (
        ("Title & Description", {
            "fields": ("title_one", "title_two", "description")
        }),
        ("Image", {
            "fields": ("image",)
        }),
        ("Stats - Open", {
            "fields": ("stat_open_label", "stat_open_value")
        }),
        ("Stats - Matches", {
            "fields": ("stat_matches_label", "stat_matches_value")
        }),
        ("Stats - Courts", {
            "fields": ("stat_courts_label", "stat_courts_value")
        }),
        ("Metadata", {
            "fields": ("updated_at",),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ["updated_at"]


@admin.register(ArenaSection)
class ArenaSectionAdmin(SingletonModelAdmin):
    """Admin interface for arena section."""
    
    fieldsets = (
        ("Content", {
            "fields": ("title", "description", "features")
        }),
        ("Metadata", {
            "fields": ("updated_at",),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ["updated_at"]


@admin.register(WhyUsSection)
class WhyUsSectionAdmin(SingletonModelAdmin):
    """Admin interface for why us section."""
    
    fieldsets = (
        ("Content", {
            "fields": ("title", "description", "features")
        }),
        ("Metadata", {
            "fields": ("updated_at",),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ["updated_at"]


@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    """Admin interface for carousel images."""
    
    list_display = ["alt_text", "sort_order", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["alt_text"]
    list_editable = ["sort_order", "is_active"]
    ordering = ["sort_order", "created_at"]
    
    fieldsets = (
        ("Image", {
            "fields": ("image", "alt_text")
        }),
        ("Display Settings", {
            "fields": ("is_active", "sort_order")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """Admin interface for testimonials."""
    
    list_display = ["full_name", "title", "is_active", "sort_order", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["full_name", "title", "content"]
    list_editable = ["is_active", "sort_order"]
    ordering = ["sort_order", "-created_at"]
    
    fieldsets = (
        ("Personal Information", {
            "fields": ("full_name", "title", "image")
        }),
        ("Content", {
            "fields": ("content",)
        }),
        ("Display Settings", {
            "fields": ("is_active", "sort_order")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ["created_at", "updated_at"]


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    """Admin interface for gallery categories."""
    
    list_display = ["name", "slug", "is_active", "sort_order", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    list_editable = ["is_active", "sort_order"]
    ordering = ["sort_order", "name"]
    prepopulated_fields = {"slug": ("name",)}
    
    fieldsets = (
        ("Category Info", {
            "fields": ("name", "slug", "description")
        }),
        ("Display Settings", {
            "fields": ("is_active", "sort_order")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ["created_at", "updated_at"]



@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    """Admin interface for gallery images."""
    
    list_display = ["title", "category", "is_active", "sort_order", "created_at"]
    list_filter = ["is_active", "category", "created_at"]
    search_fields = ["title", "alt_text"]
    list_editable = ["is_active", "sort_order"]
    ordering = ["category", "sort_order", "-created_at"]
    
    fieldsets = (
        ("Image Info", {
            "fields": ("title", "image", "alt_text", "category")
        }),
        ("Display Settings", {
            "fields": ("is_active", "sort_order")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ["created_at", "updated_at"]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')



@admin.register(GalleryHighlight)
class GalleryHighlightAdmin(admin.ModelAdmin):
    """Admin interface for gallery highlights."""
    
    list_display = ["title", "is_active", "sort_order", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["title", "tags"]
    list_editable = ["is_active", "sort_order"]
    ordering = ["sort_order", "-created_at"]
    
    fieldsets = (
        ("Video Info", {
            "fields": ("title", "video", "thumbnail", "tags")
        }),
        ("Display Settings", {
            "fields": ("is_active", "sort_order")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ["created_at", "updated_at"]


@admin.register(AboutHeroSection)
class AboutHeroSectionAdmin(SingletonModelAdmin):
    """Admin interface for about hero section."""
    
    fieldsets = (
        ("Title & Description", {
            "fields": ("title", "description")
        }),
        ("Image", {
            "fields": ("image",)
        }),
        ("Statistics", {
            "fields": ("years_in_game", "matches_hosted", "tournaments_run", "players_in_community")
        }),
        ("Metadata", {
            "fields": ("updated_at",),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ["updated_at"]


@admin.register(AboutStory)
class AboutStoryAdmin(SingletonModelAdmin):
    """Admin interface for about story section."""
    
    fieldsets = (
        ("Content", {
            "fields": ("title", "description", "image", "journey")
        }),
        ("Metadata", {
            "fields": ("updated_at",),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ["updated_at"]


@admin.register(AboutCommunity)
class AboutCommunityAdmin(SingletonModelAdmin):
    """Admin interface for about community section."""
    
    fieldsets = (
        ("Content", {
            "fields": ("title", "description", "image", "features")
        }),
        ("Team", {
            "fields": ("team",)
        }),
        ("Rules", {
            "fields": ("rules",)
        }),
        ("Metadata", {
            "fields": ("updated_at",),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ["updated_at"]


@admin.register(BookingsHeroSection)
class BookingsHeroSectionAdmin(SingletonModelAdmin):
    """Admin interface for bookings hero section."""
    
    fieldsets = (
        ("Title & Description", {
            "fields": ("title", "description")
        }),
        ("Image", {
            "fields": ("image",)
        }),
        ("Info", {
            "fields": ("info",)
        }),
        ("Metadata", {
            "fields": ("updated_at",),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ["updated_at"]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["question", "created_at", "updated_at"]
    search_fields = ["question", "answer"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(TermsAndPrivacy)
class TermsAndPrivacyAdmin(SingletonModelAdmin):
    fieldsets = (
        ("Legal Content", {"fields": ("terms", "privacy")}),
        ("Metadata", {"fields": ("updated_at",), "classes": ("collapse",)}),
    )
    readonly_fields = ["updated_at"]
