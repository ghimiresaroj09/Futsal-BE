"""CMS models for managing homepage and static content."""
from __future__ import annotations

from django.db import models

from common.models import BaseModel
from common.storages import image_storage, video_storage
from common.validators import validate_image_upload, validate_video_upload


class HomepageMeta(BaseModel):
    """Singleton model for homepage SEO metadata."""
    
    meta_title = models.CharField(max_length=200, default="Nexus FMS — Book Your Futsal Slot Online")
    meta_description = models.TextField(
        max_length=300,
        default="Premium futsal courts in Kathmandu. Check live availability and book your slot online in seconds — pay at the counter."
    )
    
    class Meta:
        db_table = "cms_homepage_meta"
        verbose_name = "Homepage Meta"
        verbose_name_plural = "Homepage Meta"
    
    def __str__(self) -> str:
        return "Homepage Meta"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "HomepageMeta":
        """Get or create the singleton instance."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class HeroSection(BaseModel):
    """Homepage hero section content."""
    
    badge = models.CharField(max_length=100, default="Kathmandu's home of futsal")
    title = models.CharField(max_length=100, default="Book your slot.")
    title_highlight = models.CharField(
        max_length=100, default="Own the game.", blank=True,
        help_text="Highlighted part of the title (optional)"
    )
    description = models.TextField()
    image = models.ImageField(
        upload_to="cms/hero/", storage=image_storage,
        validators=[validate_image_upload], blank=True, null=True
    )
    image_alt = models.CharField(max_length=200, blank=True)
    primary_cta_label = models.CharField(max_length=50, default="Book a Slot")
    primary_cta_href = models.CharField(max_length=200, default="/bookings")
    primary_cta_style = models.CharField(max_length=20, default="primary")
    secondary_cta_label = models.CharField(max_length=50, default="Explore Gallery")
    secondary_cta_href = models.CharField(max_length=200, default="/gallery")
    secondary_cta_style = models.CharField(max_length=20, default="outline")
    
    class Meta:
        db_table = "cms_hero_section"
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Section"
    
    def __str__(self) -> str:
        return "Hero Section"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "HeroSection":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class StatItem(BaseModel):
    """Homepage statistics items."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True)
    value = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_stat_item"
        ordering = ["sort_order", "created_at"]
        verbose_name = "Stat Item"
        verbose_name_plural = "Stat Items"
    
    def __str__(self) -> str:
        return f"{self.key}: {self.value}"


class ArenaSection(BaseModel):
    """Homepage arena section content."""
    
    eyebrow = models.CharField(max_length=50, default="The Arena")
    heading = models.CharField(max_length=100, default="One arena. Built for the game.")
    description = models.TextField()
    since_label = models.CharField(max_length=50, default="Since 2018")
    
    class Meta:
        db_table = "cms_arena_section"
        verbose_name = "Arena Section"
        verbose_name_plural = "Arena Section"
    
    def __str__(self) -> str:
        return "Arena Section"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "ArenaSection":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ArenaHighlight(BaseModel):
    """Arena section highlights/features."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True)
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Icon name (e.g., 'sparkles', 'zap')")
    text = models.CharField(max_length=200)
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_arena_highlight"
        ordering = ["sort_order", "created_at"]
        verbose_name = "Arena Highlight"
        verbose_name_plural = "Arena Highlights"
    
    def __str__(self) -> str:
        return self.text


class ArenaImage(BaseModel):
    """Arena section images for carousel."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True)
    image = models.ImageField(
        upload_to="cms/arena/", storage=image_storage,
        validators=[validate_image_upload]
    )
    alt_text = models.CharField(max_length=200)
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_arena_image"
        ordering = ["sort_order", "created_at"]
        verbose_name = "Arena Image"
        verbose_name_plural = "Arena Images"
    
    def __str__(self) -> str:
        return self.alt_text


class FeaturesSection(BaseModel):
    """Homepage features section header."""
    
    eyebrow = models.CharField(max_length=50, default="Why Nexus")
    heading = models.CharField(max_length=100, default="Everything a player needs")
    
    class Meta:
        db_table = "cms_features_section"
        verbose_name = "Features Section"
        verbose_name_plural = "Features Section"
    
    def __str__(self) -> str:
        return "Features Section"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "FeaturesSection":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class FeatureItem(BaseModel):
    """Individual feature items."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True)
    icon = models.CharField(max_length=50, help_text="Icon name")
    title = models.CharField(max_length=100)
    description = models.TextField()
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_feature_item"
        ordering = ["sort_order", "created_at"]
        verbose_name = "Feature Item"
        verbose_name_plural = "Feature Items"
    
    def __str__(self) -> str:
        return self.title


class HowItWorksSection(BaseModel):
    """Homepage 'How it works' section header."""
    
    eyebrow = models.CharField(max_length=50, default="How it works")
    heading = models.CharField(max_length=100, default="On the pitch in three steps")
    
    class Meta:
        db_table = "cms_how_it_works_section"
        verbose_name = "How It Works Section"
        verbose_name_plural = "How It Works Section"
    
    def __str__(self) -> str:
        return "How It Works Section"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "HowItWorksSection":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class HowItWorksStep(BaseModel):
    """Steps in the 'How it works' section."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True)
    icon = models.CharField(max_length=50, help_text="Icon name")
    title = models.CharField(max_length=100)
    description = models.TextField()
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_how_it_works_step"
        ordering = ["sort_order", "created_at"]
        verbose_name = "How It Works Step"
        verbose_name_plural = "How It Works Steps"
    
    def __str__(self) -> str:
        return self.title


class GalleryPreviewSection(BaseModel):
    """Homepage gallery preview section header."""
    
    eyebrow = models.CharField(max_length=50, default="Gallery")
    heading = models.CharField(max_length=100, default="Straight off our turf")
    description = models.TextField()
    count_label = models.CharField(max_length=50, default="+120 photos")
    cta_label = models.CharField(max_length=50, default="View full gallery")
    cta_href = models.CharField(max_length=200, default="/gallery")
    cta_style = models.CharField(max_length=20, default="outline")
    
    class Meta:
        db_table = "cms_gallery_preview_section"
        verbose_name = "Gallery Preview Section"
        verbose_name_plural = "Gallery Preview Section"
    
    def __str__(self) -> str:
        return "Gallery Preview Section"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "GalleryPreviewSection":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class GalleryPreviewPhoto(BaseModel):
    """Photos in the gallery preview section."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True)
    image = models.ImageField(
        upload_to="cms/gallery/", storage=image_storage,
        validators=[validate_image_upload]
    )
    alt_text = models.CharField(max_length=200)
    aspect_ratio = models.CharField(max_length=10, default="4/3", help_text="e.g., '4/3', '16/9', '1/1'")
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_gallery_preview_photo"
        ordering = ["sort_order", "created_at"]
        verbose_name = "Gallery Preview Photo"
        verbose_name_plural = "Gallery Preview Photos"
    
    def __str__(self) -> str:
        return self.alt_text


class TestimonialsSection(BaseModel):
    """Homepage testimonials section header."""
    
    eyebrow = models.CharField(max_length=50, default="Testimonials")
    heading = models.CharField(max_length=100, default="What our players say")
    
    class Meta:
        db_table = "cms_testimonials_section"
        verbose_name = "Testimonials Section"
        verbose_name_plural = "Testimonials Section"
    
    def __str__(self) -> str:
        return "Testimonials Section"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "TestimonialsSection":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Testimonial(BaseModel):
    """Individual testimonial items."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True)
    quote = models.TextField()
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    avatar = models.ImageField(
        upload_to="cms/testimonials/", storage=image_storage,
        validators=[validate_image_upload], blank=True, null=True
    )
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_testimonial"
        ordering = ["sort_order", "created_at"]
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
    
    def __str__(self) -> str:
        return f"{self.name} - {self.role}"


class CTABannerSection(BaseModel):
    """Homepage CTA banner section."""
    
    heading = models.CharField(max_length=200, default="Gather your squad. We'll keep the lights on.")
    description = models.TextField()
    primary_cta_label = models.CharField(max_length=50, default="Book a Slot")
    primary_cta_href = models.CharField(max_length=200, default="/bookings")
    primary_cta_style = models.CharField(max_length=20, default="secondary")
    secondary_cta_label = models.CharField(max_length=50, default="Contact Us")
    secondary_cta_href = models.CharField(max_length=200, default="/contact")
    secondary_cta_style = models.CharField(max_length=20, default="outline")
    
    class Meta:
        db_table = "cms_cta_banner_section"
        verbose_name = "CTA Banner Section"
        verbose_name_plural = "CTA Banner Section"
    
    def __str__(self) -> str:
        return "CTA Banner Section"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "CTABannerSection":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ============================================================================
# Bookings Page Models
# ============================================================================


class BookingsPageMeta(BaseModel):
    """Singleton model for bookings page SEO metadata."""
    
    meta_title = models.CharField(max_length=200, default="Book a Slot — Nexus FMS")
    meta_description = models.TextField(
        max_length=300,
        default="Check live slot availability and book your futsal court online. Pay at the counter — free rescheduling up to 12 hours before."
    )
    
    class Meta:
        db_table = "cms_bookings_page_meta"
        verbose_name = "Bookings Page Meta"
        verbose_name_plural = "Bookings Page Meta"
    
    def __str__(self) -> str:
        return "Bookings Page Meta"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "BookingsPageMeta":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class BookingsBanner(BaseModel):
    """Bookings page banner section."""
    
    eyebrow = models.CharField(max_length=50, default="Bookings")
    title = models.CharField(max_length=200, default="Pick your date. Own your slot.")
    description = models.TextField()
    image = models.ImageField(
        upload_to="cms/bookings/", storage=image_storage,
        validators=[validate_image_upload], blank=True, null=True
    )
    image_alt = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = "cms_bookings_banner"
        verbose_name = "Bookings Banner"
        verbose_name_plural = "Bookings Banner"
    
    def __str__(self) -> str:
        return "Bookings Banner"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "BookingsBanner":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class BookingsStepsSection(BaseModel):
    """Bookings page how-it-works steps header."""
    
    heading = models.CharField(max_length=100, default="How booking works")
    
    class Meta:
        db_table = "cms_bookings_steps_section"
        verbose_name = "Bookings Steps Section"
        verbose_name_plural = "Bookings Steps Section"
    
    def __str__(self) -> str:
        return "Bookings Steps Section"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "BookingsStepsSection":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class BookingsStep(BaseModel):
    """Steps in the bookings how-it-works section."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_bookings_step"
        ordering = ["sort_order", "created_at"]
        verbose_name = "Bookings Step"
        verbose_name_plural = "Bookings Steps"
    
    def __str__(self) -> str:
        return self.title


class BookingsRatesSection(BaseModel):
    """Bookings page rates section."""
    
    heading = models.CharField(max_length=100, default="Rates")
    description = models.TextField()
    weekday_label = models.CharField(max_length=50, default="Weekday")
    weekend_label = models.CharField(max_length=50, default="Weekend")
    refreshments_note = models.TextField()
    
    # Events subsection
    events_title = models.CharField(max_length=100, default="Full arena & events")
    events_description = models.TextField()
    events_cta_label = models.CharField(max_length=50, default="Contact us")
    events_cta_href = models.CharField(max_length=200, default="/contact")
    events_cta_style = models.CharField(max_length=20, default="outline")
    
    class Meta:
        db_table = "cms_bookings_rates_section"
        verbose_name = "Bookings Rates Section"
        verbose_name_plural = "Bookings Rates Section"
    
    def __str__(self) -> str:
        return "Bookings Rates Section"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "BookingsRatesSection":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class BookingsRateRow(BaseModel):
    """Rate matrix rows."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=100)
    hours = models.CharField(max_length=50, help_text="e.g., '6 AM – 12 PM'")
    weekday_price = models.PositiveIntegerField(help_text="Price in NPR")
    weekend_price = models.PositiveIntegerField(help_text="Price in NPR")
    highlight = models.BooleanField(default=False)
    highlight_label = models.CharField(max_length=50, blank=True, help_text="e.g., 'Floodlit'")
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_bookings_rate_row"
        ordering = ["sort_order", "created_at"]
        verbose_name = "Bookings Rate Row"
        verbose_name_plural = "Bookings Rate Rows"
    
    def __str__(self) -> str:
        return f"{self.title} ({self.hours})"


class BookingsPoliciesSection(BaseModel):
    """Bookings page policies section header."""
    
    heading = models.CharField(max_length=100, default="Good to know")
    
    class Meta:
        db_table = "cms_bookings_policies_section"
        verbose_name = "Bookings Policies Section"
        verbose_name_plural = "Bookings Policies Section"
    
    def __str__(self) -> str:
        return "Bookings Policies Section"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "BookingsPoliciesSection":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class BookingsPolicy(BaseModel):
    """Policy items (e.g., free rescheduling)."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True)
    icon = models.CharField(max_length=50, help_text="Icon name")
    title = models.CharField(max_length=100)
    description = models.TextField()
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_bookings_policy"
        ordering = ["sort_order", "created_at"]
        verbose_name = "Bookings Policy"
        verbose_name_plural = "Bookings Policies"
    
    def __str__(self) -> str:
        return self.title


class BookingsHelpStrip(BaseModel):
    """Bookings page help strip section."""
    
    heading = models.CharField(max_length=200, default="Need a hand with your booking?")
    description = models.TextField()
    cta_label = models.CharField(max_length=50, default="Contact Us")
    cta_href = models.CharField(max_length=200, default="/contact")
    cta_style = models.CharField(max_length=20, default="outline")
    
    class Meta:
        db_table = "cms_bookings_help_strip"
        verbose_name = "Bookings Help Strip"
        verbose_name_plural = "Bookings Help Strip"
    
    def __str__(self) -> str:
        return "Bookings Help Strip"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "BookingsHelpStrip":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ============================================================================
# Gallery Page Models
# ============================================================================


class GalleryPageMeta(BaseModel):
    """Singleton model for gallery page SEO metadata."""
    
    meta_title = models.CharField(max_length=200, default="Gallery — Nexus FMS")
    meta_description = models.TextField(
        max_length=300,
        default="Photos and clips from the Nexus Futsal community — match nights, coaching mornings and the turf itself."
    )
    
    class Meta:
        db_table = "cms_gallery_page_meta"
        verbose_name = "Gallery Page Meta"
        verbose_name_plural = "Gallery Page Meta"
    
    def __str__(self) -> str:
        return "Gallery Page Meta"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "GalleryPageMeta":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class GalleryHeader(BaseModel):
    """Gallery page header section."""
    
    eyebrow = models.CharField(max_length=50, default="Gallery")
    title = models.CharField(max_length=200, default="The arena, up close")
    description = models.TextField()
    
    class Meta:
        db_table = "cms_gallery_header"
        verbose_name = "Gallery Header"
        verbose_name_plural = "Gallery Header"
    
    def __str__(self) -> str:
        return "Gallery Header"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "GalleryHeader":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class GalleryCategory(BaseModel):
    """Gallery photo/video categories for filtering."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True, help_text="Uppercase enum (e.g., 'ALL', 'VENUE', 'MATCHES')")
    label = models.CharField(max_length=100, help_text="Display label (e.g., 'All', 'Our Venue')")
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_gallery_category"
        ordering = ["sort_order", "created_at"]
        verbose_name = "Gallery Category"
        verbose_name_plural = "Gallery Categories"
    
    def __str__(self) -> str:
        return self.label


class GalleryPhoto(BaseModel):
    """Gallery photos."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True)
    image = models.ImageField(
        upload_to="cms/gallery/photos/", storage=image_storage,
        validators=[validate_image_upload]
    )
    alt_text = models.CharField(max_length=200, help_text="Alt text for accessibility")
    title = models.CharField(max_length=200, help_text="Title shown on hover")
    category = models.CharField(max_length=50, db_index=True, help_text="Category key (e.g., 'VENUE', 'MATCHES')")
    aspect_ratio = models.CharField(max_length=10, default="4/3", help_text="e.g., '16/10', '4/3', '1/1', '3/4'")
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_gallery_photo"
        ordering = ["sort_order", "created_at"]
        verbose_name = "Gallery Photo"
        verbose_name_plural = "Gallery Photos"
        indexes = [models.Index(fields=["category", "is_active"])]
    
    def __str__(self) -> str:
        return self.title


class GalleryVideosSection(BaseModel):
    """Gallery videos section header."""
    
    heading = models.CharField(max_length=100, default="Highlights & clips")
    description = models.TextField(default="Short clips from around the arena — press play.")
    
    class Meta:
        db_table = "cms_gallery_videos_section"
        verbose_name = "Gallery Videos Section"
        verbose_name_plural = "Gallery Videos Section"
    
    def __str__(self) -> str:
        return "Gallery Videos Section"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "GalleryVideosSection":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class GalleryVideo(BaseModel):
    """Gallery video clips."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True)
    video = models.FileField(
        upload_to="cms/gallery/videos/", storage=video_storage,
        validators=[validate_video_upload]
    )
    poster = models.ImageField(
        upload_to="cms/gallery/posters/", storage=image_storage,
        validators=[validate_image_upload], help_text="Video thumbnail/poster"
    )
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, db_index=True, help_text="Category key (e.g., 'VENUE', 'MATCHES')")
    duration_seconds = models.PositiveIntegerField(help_text="Video duration in seconds")
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_gallery_video"
        ordering = ["sort_order", "created_at"]
        verbose_name = "Gallery Video"
        verbose_name_plural = "Gallery Videos"
        indexes = [models.Index(fields=["category", "is_active"])]
    
    def __str__(self) -> str:
        return self.title


class GalleryCTA(BaseModel):
    """Gallery page closing CTA."""
    
    heading = models.CharField(max_length=200, default="Pictures are nice. Playing is nicer.")
    description = models.TextField()
    button_label = models.CharField(max_length=50, default="Book a Slot")
    button_href = models.CharField(max_length=200, default="/bookings")
    button_style = models.CharField(max_length=20, default="primary")
    
    class Meta:
        db_table = "cms_gallery_cta"
        verbose_name = "Gallery CTA"
        verbose_name_plural = "Gallery CTA"
    
    def __str__(self) -> str:
        return "Gallery CTA"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "GalleryCTA":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ============================================================================
# ABOUT PAGE MODELS
# ============================================================================

class AboutPageMeta(BaseModel):
    """Singleton model for About page SEO metadata."""
    
    meta_title = models.CharField(max_length=200, default="About Us — Nexus FMS")
    meta_description = models.TextField(
        max_length=300,
        default="Since 2018, Nexus Futsal has been Kathmandu's home of futsal. Meet the team, the story and the community behind the turf."
    )
    
    class Meta:
        db_table = "cms_about_meta"
        verbose_name = "About Page Meta"
        verbose_name_plural = "About Page Meta"
    
    def __str__(self) -> str:
        return "About Page Meta"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "AboutPageMeta":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AboutHero(BaseModel):
    """About page hero section."""
    
    eyebrow = models.CharField(max_length=100, default="About us")
    title = models.CharField(max_length=200, default="More than a court.")
    title_highlight = models.CharField(max_length=200, default="A community.")
    description = models.TextField()
    image = models.ImageField(
        upload_to="cms/about/hero/", storage=image_storage,
        validators=[validate_image_upload]
    )
    image_alt = models.CharField(max_length=200)
    
    class Meta:
        db_table = "cms_about_hero"
        verbose_name = "About Hero"
        verbose_name_plural = "About Hero"
    
    def __str__(self) -> str:
        return "About Hero"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "AboutHero":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AboutStat(BaseModel):
    """About page statistics."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True, help_text="e.g., 'years', 'matches'")
    value = models.CharField(max_length=50, help_text="e.g., '8+', '20K+'")
    label = models.CharField(max_length=100, help_text="e.g., 'Years in the game'")
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_about_stat"
        ordering = ["sort_order", "created_at"]
        verbose_name = "About Stat"
        verbose_name_plural = "About Stats"
    
    def __str__(self) -> str:
        return f"{self.key}: {self.value}"


class AboutStory(BaseModel):
    """About page story section."""
    
    eyebrow = models.CharField(max_length=100, default="Our story")
    heading = models.CharField(max_length=200, default="Built by players, for players")
    description = models.TextField()
    timeline_heading = models.CharField(max_length=200, default="The journey so far")
    timeline_hint = models.CharField(
        max_length=300, blank=True,
        default="Drag the cards or use the arrows — the story continues →"
    )
    
    class Meta:
        db_table = "cms_about_story"
        verbose_name = "About Story"
        verbose_name_plural = "About Story"
    
    def __str__(self) -> str:
        return "About Story"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "AboutStory":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AboutMilestone(BaseModel):
    """About page timeline milestones."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True)
    year = models.CharField(max_length=10, help_text="e.g., '2018', '2021'")
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(
        upload_to="cms/about/milestones/", storage=image_storage,
        validators=[validate_image_upload]
    )
    image_alt = models.CharField(max_length=200)
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_about_milestone"
        ordering = ["sort_order", "created_at"]
        verbose_name = "About Milestone"
        verbose_name_plural = "About Milestones"
    
    def __str__(self) -> str:
        return f"{self.year}: {self.title}"


class AboutValues(BaseModel):
    """About page values section header."""
    
    eyebrow = models.CharField(max_length=100, default="What we stand for")
    heading = models.CharField(max_length=200, default="The values on our badge")
    
    class Meta:
        db_table = "cms_about_values"
        verbose_name = "About Values"
        verbose_name_plural = "About Values"
    
    def __str__(self) -> str:
        return "About Values"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "AboutValues":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AboutValue(BaseModel):
    """About page individual values."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True, help_text="e.g., 'community', 'facilities'")
    icon = models.CharField(max_length=50, help_text="Icon name from shared registry, e.g., 'heart-handshake'")
    title = models.CharField(max_length=200)
    description = models.TextField()
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_about_value"
        ordering = ["sort_order", "created_at"]
        verbose_name = "About Value"
        verbose_name_plural = "About Values"
    
    def __str__(self) -> str:
        return self.title


class AboutCommunity(BaseModel):
    """About page community section."""
    
    eyebrow = models.CharField(max_length=100, default="Community")
    heading = models.CharField(max_length=200, default="The arena fills up long before kickoff")
    description = models.TextField()
    image = models.ImageField(
        upload_to="cms/about/community/", storage=image_storage,
        validators=[validate_image_upload]
    )
    image_alt = models.CharField(max_length=200)
    
    class Meta:
        db_table = "cms_about_community"
        verbose_name = "About Community"
        verbose_name_plural = "About Community"
    
    def __str__(self) -> str:
        return "About Community"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "AboutCommunity":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AboutCommunityBullet(BaseModel):
    """About page community bullet points."""
    
    text = models.TextField()
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_about_community_bullet"
        ordering = ["sort_order", "created_at"]
        verbose_name = "About Community Bullet"
        verbose_name_plural = "About Community Bullets"
    
    def __str__(self) -> str:
        return self.text[:50]


class AboutTeam(BaseModel):
    """About page team section header."""
    
    eyebrow = models.CharField(max_length=100, default="The team")
    heading = models.CharField(max_length=200, default="The people behind the turf")
    description = models.TextField(default="Say hi when you see us at the counter — we're usually around.")
    
    class Meta:
        db_table = "cms_about_team"
        verbose_name = "About Team"
        verbose_name_plural = "About Team"
    
    def __str__(self) -> str:
        return "About Team"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "AboutTeam":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AboutTeamMember(BaseModel):
    """About page team members."""
    
    key = models.CharField(max_length=50, unique=True, db_index=True)
    full_name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    profile_image = models.ImageField(
        upload_to="cms/about/team/", storage=image_storage,
        validators=[validate_image_upload], blank=True, null=True,
        help_text="Leave blank to show initials avatar"
    )
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_about_team_member"
        ordering = ["sort_order", "created_at"]
        verbose_name = "About Team Member"
        verbose_name_plural = "About Team Members"
    
    def __str__(self) -> str:
        return f"{self.full_name} - {self.role}"


class AboutCTA(BaseModel):
    """About page closing CTA banner."""
    
    heading = models.CharField(max_length=200, default="Come see the turf for yourself")
    description = models.TextField()
    primary_cta_label = models.CharField(max_length=50, default="Book a Slot")
    primary_cta_href = models.CharField(max_length=200, default="/bookings")
    primary_cta_style = models.CharField(max_length=20, default="secondary")
    secondary_cta_label = models.CharField(max_length=50, default="Contact Us")
    secondary_cta_href = models.CharField(max_length=200, default="/contact")
    secondary_cta_style = models.CharField(max_length=20, default="outline")
    
    class Meta:
        db_table = "cms_about_cta"
        verbose_name = "About CTA"
        verbose_name_plural = "About CTA"
    
    def __str__(self) -> str:
        return "About CTA"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "AboutCTA":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj



# ============================================================================
# CONTACT PAGE MODELS
# ============================================================================

class ContactPageMeta(BaseModel):
    """Singleton model for Contact page SEO metadata."""
    
    meta_title = models.CharField(max_length=200, default="Contact Us — Nexus FMS")
    meta_description = models.TextField(
        max_length=300,
        default="Questions about bookings, events or coaching? Reach the Nexus Futsal team by phone, email or the contact form."
    )
    
    class Meta:
        db_table = "cms_contact_meta"
        verbose_name = "Contact Page Meta"
        verbose_name_plural = "Contact Page Meta"
    
    def __str__(self) -> str:
        return "Contact Page Meta"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "ContactPageMeta":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ContactHeader(BaseModel):
    """Contact page header section."""
    
    eyebrow = models.CharField(max_length=100, default="Contact Us")
    title = models.CharField(max_length=200, default="We'd love to hear from you")
    description = models.TextField()
    
    class Meta:
        db_table = "cms_contact_header"
        verbose_name = "Contact Header"
        verbose_name_plural = "Contact Header"
    
    def __str__(self) -> str:
        return "Contact Header"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "ContactHeader":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ContactForm(BaseModel):
    """Contact page form section."""
    
    heading = models.CharField(max_length=200, default="Send us a message")
    description = models.TextField(default="Fill in the form below — we usually reply within a couple of hours.")
    submit_label = models.CharField(max_length=50, default="Send Message")
    submitting_label = models.CharField(max_length=50, default="Sending…")
    success_title = models.CharField(max_length=200, default="Message sent!")
    success_description = models.TextField(
        default="Thanks {first_name} — we'll reply to {email} within a few hours during opening times.",
        help_text="Supports tokens: {first_name}, {email}"
    )
    again_label = models.CharField(max_length=50, default="Send another message")
    
    # Field labels
    name_label = models.CharField(max_length=100, default="Full name")
    name_placeholder = models.CharField(max_length=200, default="Enter your full name")
    
    email_label = models.CharField(max_length=100, default="Email")
    email_placeholder = models.CharField(max_length=200, default="you@example.com")
    
    phone_label = models.CharField(max_length=100, default="Phone number")
    phone_placeholder = models.CharField(max_length=200, default="10-digit mobile number")
    
    subject_label = models.CharField(max_length=100, default="Subject")
    subject_placeholder = models.CharField(max_length=200, default="e.g. Corporate event on a Saturday")
    
    message_label = models.CharField(max_length=100, default="Message")
    message_placeholder = models.CharField(max_length=200, default="Tell us what's on your mind")
    
    class Meta:
        db_table = "cms_contact_form"
        verbose_name = "Contact Form"
        verbose_name_plural = "Contact Form"
    
    def __str__(self) -> str:
        return "Contact Form"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "ContactForm":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ContactDetails(BaseModel):
    """Contact page details section."""
    
    heading = models.CharField(max_length=200, default="Reach us directly")
    description = models.TextField(default="The counter is staffed whenever the lights are on.")
    maps_label = models.CharField(max_length=100, default="Get directions")
    
    class Meta:
        db_table = "cms_contact_details"
        verbose_name = "Contact Details"
        verbose_name_plural = "Contact Details"
    
    def __str__(self) -> str:
        return "Contact Details"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "ContactDetails":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ContactDetailItem(BaseModel):
    """Contact page detail items."""
    
    ITEM_TYPES = [
        ('VISIT', 'Visit'),
        ('CALL', 'Call'),
        ('EMAIL', 'Email'),
        ('HOURS', 'Hours'),
    ]
    
    key = models.CharField(max_length=50, unique=True, db_index=True)
    item_type = models.CharField(
        max_length=20, choices=ITEM_TYPES, db_index=True,
        help_text="Controls icon + link behavior"
    )
    label = models.CharField(max_length=100)
    hint = models.CharField(
        max_length=300, blank=True,
        help_text="Small muted line under the value (optional)"
    )
    value_source = models.CharField(
        max_length=200,
        help_text="Documentation: which futsal field feeds the value (e.g., 'futsal.phone')"
    )
    sort_order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "cms_contact_detail_item"
        ordering = ["sort_order", "created_at"]
        verbose_name = "Contact Detail Item"
        verbose_name_plural = "Contact Detail Items"
    
    def __str__(self) -> str:
        return f"{self.label} ({self.item_type})"


class ContactBookingCard(BaseModel):
    """Contact page booking nudge card."""
    
    title = models.CharField(max_length=200, default="Looking to book instead?")
    description = models.TextField(default="Skip the queue — pick your slot online and pay at the counter.")
    cta_label = models.CharField(max_length=50, default="Book a Slot")
    cta_href = models.CharField(max_length=200, default="/bookings")
    cta_style = models.CharField(max_length=20, default="primary")
    
    class Meta:
        db_table = "cms_contact_booking_card"
        verbose_name = "Contact Booking Card"
        verbose_name_plural = "Contact Booking Card"
    
    def __str__(self) -> str:
        return "Contact Booking Card"
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls) -> "ContactBookingCard":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
