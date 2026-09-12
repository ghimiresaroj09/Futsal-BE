"""CMS models for testimonials and other content."""
from __future__ import annotations

from django.db import models
from solo.models import SingletonModel

from common.models import BaseModel
from common.storages import image_storage, video_storage


class HeroSection(SingletonModel):
    """Homepage hero section content (singleton)."""
    
    title_one = models.CharField(max_length=200, help_text="First line of title")
    title_two = models.CharField(max_length=200, help_text="Second line of title")
    description = models.TextField(help_text="Hero description text")
    image = models.ImageField(
        upload_to="hero/",
        storage=image_storage,
        help_text="Hero background image",
        null=True,
        blank=True
    )
    
    # Stats
    stat_open_label = models.CharField(max_length=100, default="Open every day", help_text="Stat 1 label")
    stat_open_value = models.CharField(max_length=50, default="7 Days/Week", help_text="Stat 1 value")
    
    stat_matches_label = models.CharField(max_length=100, default="Matches hosted", help_text="Stat 2 label")
    stat_matches_value = models.CharField(max_length=50, default="500+", help_text="Stat 2 value")
    
    stat_courts_label = models.CharField(max_length=100, default="Premium courts", help_text="Stat 3 label")
    stat_courts_value = models.CharField(max_length=50, default="2 Courts", help_text="Stat 3 value")
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Section"
    
    def __str__(self):
        return "Homepage Hero Section"


class CarouselImage(BaseModel):
    """Carousel image for homepage."""
    
    image = models.ImageField(
        upload_to="carousel/",
        storage=image_storage,
        help_text="Carousel image"
    )
    alt_text = models.CharField(
        max_length=200,
        help_text="Alt text for accessibility"
    )
    sort_order = models.IntegerField(
        default=0,
        help_text="Display order (lower numbers first)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Show in carousel"
    )
    
    class Meta:
        db_table = "cms_carousel_image"
        ordering = ["sort_order", "created_at"]
        verbose_name = "Carousel Image"
        verbose_name_plural = "Carousel Images"
    
    def __str__(self):
        return f"Carousel Image {self.sort_order} - {self.alt_text[:50]}"


class ArenaSection(SingletonModel):
    """Homepage arena section content (singleton)."""
    
    title = models.CharField(max_length=200, help_text="Arena section title")
    description = models.TextField(help_text="Arena description text")
    features = models.JSONField(
        default=list,
        help_text="Array of feature strings",
        blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Arena Section"
        verbose_name_plural = "Arena Section"
    
    def __str__(self):
        return "Homepage Arena Section"


class WhyUsSection(SingletonModel):
    """Homepage why us section content (singleton)."""
    
    title = models.CharField(max_length=200, help_text="Why us section title")
    description = models.TextField(help_text="Why us description text")
    features = models.JSONField(
        default=list,
        help_text="Array of feature objects with iconcode, title, and description",
        blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Why Us Section"
        verbose_name_plural = "Why Us Section"
    
    def __str__(self):
        return "Homepage Why Us Section"


class GalleryCategory(BaseModel):
    """Gallery category for organizing images and videos."""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (e.g., 'Tournaments', 'Facilities', 'Events')"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly version of name"
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Optional category description"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Show category on website"
    )
    sort_order = models.IntegerField(
        default=0,
        help_text="Display order (lower numbers first)"
    )
    
    class Meta:
        db_table = "cms_gallery_category"
        ordering = ["sort_order", "name"]
        verbose_name = "Gallery Category"
        verbose_name_plural = "Gallery Categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class GalleryImage(BaseModel):
    """Gallery image with category."""
    
    title = models.CharField(
        max_length=200,
        help_text="Image title"
    )
    image = models.ImageField(
        upload_to="gallery/",
        storage=image_storage,
        help_text="Gallery image"
    )
    alt_text = models.CharField(
        max_length=200,
        help_text="Alt text for accessibility"
    )
    category = models.ForeignKey(
        GalleryCategory,
        on_delete=models.CASCADE,
        related_name="images",
        help_text="Gallery category"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Show on website"
    )
    sort_order = models.IntegerField(
        default=0,
        help_text="Display order within category"
    )
    
    class Meta:
        db_table = "cms_gallery_image"
        ordering = ["category", "sort_order", "created_at"]
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["category", "sort_order"]),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.category.name})"


class GalleryHighlight(BaseModel):
    """Gallery highlight video."""
    
    title = models.CharField(
        max_length=200,
        help_text="Video title"
    )
    video = models.FileField(
        upload_to="highlights/",
        storage=video_storage,
        help_text="Highlight video (Cloudinary)"
    )
    tags = models.TextField(
        blank=True,
        default="",
        help_text="Tags for the video (e.g., 'goal, save, skills')"
    )
    thumbnail = models.ImageField(
        upload_to="highlights/thumbnails/",
        storage=image_storage,
        null=True,
        blank=True,
        help_text="Video thumbnail (optional)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Show on website"
    )
    sort_order = models.IntegerField(
        default=0,
        help_text="Display order"
    )
    
    class Meta:
        db_table = "cms_gallery_highlight"
        ordering = ["sort_order", "-created_at"]
        verbose_name = "Gallery Highlight"
        verbose_name_plural = "Gallery Highlights"
        indexes = [
            models.Index(fields=["is_active", "sort_order"]),
        ]
    
    def __str__(self):
        return self.title


class Testimonial(BaseModel):
    """Customer testimonial for the website."""
    
    full_name = models.CharField(max_length=200, help_text="Customer's full name")
    title = models.CharField(max_length=200, help_text="Job title or role (e.g., 'Regular Player', 'Tournament Organizer')")
    image = models.ImageField(
        upload_to="testimonials/",
        storage=image_storage,
        help_text="Customer photo",
        null=True,
        blank=True
    )
    content = models.TextField(help_text="Testimonial content/review")
    is_active = models.BooleanField(default=True, help_text="Show on website")
    sort_order = models.IntegerField(default=0, help_text="Display order (lower numbers first)")
    
    class Meta:
        db_table = "cms_testimonial"
        ordering = ["sort_order", "-created_at"]
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
    
    def __str__(self):
        return f"{self.full_name} - {self.title}"


class AboutHeroSection(SingletonModel):
    """About page hero section content (singleton)."""
    
    title = models.CharField(max_length=200, help_text="About hero section title")
    description = models.TextField(help_text="About hero description text")
    image = models.ImageField(
        upload_to="about/hero/",
        storage=image_storage,
        help_text="About hero background image",
        null=True,
        blank=True
    )
    
    # Stats
    years_in_game = models.IntegerField(default=0, help_text="Years in the game")
    matches_hosted = models.IntegerField(default=0, help_text="Matches hosted")
    tournaments_run = models.IntegerField(default=0, help_text="Tournaments run")
    players_in_community = models.IntegerField(default=0, help_text="Players in the community")
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "About Hero Section"
        verbose_name_plural = "About Hero Section"
    
    def __str__(self):
        return "About Page Hero Section"
