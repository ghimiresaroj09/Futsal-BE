"""CMS serializers for homepage content."""
from __future__ import annotations

from rest_framework import serializers


class CTASerializer(serializers.Serializer):
    """Call-to-action button serializer."""
    label = serializers.CharField()
    href = serializers.CharField()
    style = serializers.CharField()


class ImageSerializer(serializers.Serializer):
    """Image with URL and alt text."""
    url = serializers.URLField()
    alt = serializers.CharField()


class HeroSectionSerializer(serializers.Serializer):
    """Hero section serializer."""
    badge = serializers.CharField()
    title = serializers.CharField()
    title_highlight = serializers.CharField(allow_blank=True, allow_null=True)
    description = serializers.CharField()
    image = ImageSerializer()
    primary_cta = CTASerializer()
    secondary_cta = CTASerializer()


class StatItemSerializer(serializers.Serializer):
    """Statistics item serializer."""
    id = serializers.CharField(source='key')
    value = serializers.CharField()
    label = serializers.CharField()


class ArenaHighlightSerializer(serializers.Serializer):
    """Arena highlight item serializer."""
    id = serializers.CharField(source='key')
    icon = serializers.CharField(allow_null=True)
    text = serializers.CharField()


class ArenaImageSerializer(serializers.Serializer):
    """Arena image serializer."""
    id = serializers.CharField(source='key')
    url = serializers.URLField()
    alt = serializers.CharField(source='alt_text')


class ArenaSectionSerializer(serializers.Serializer):
    """Arena section serializer."""
    eyebrow = serializers.CharField()
    heading = serializers.CharField()
    description = serializers.CharField()
    since_label = serializers.CharField()
    highlights = ArenaHighlightSerializer(many=True)
    images = ArenaImageSerializer(many=True)


class FeatureItemSerializer(serializers.Serializer):
    """Feature item serializer."""
    id = serializers.CharField(source='key')
    icon = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()


class FeaturesSectionSerializer(serializers.Serializer):
    """Features section serializer."""
    eyebrow = serializers.CharField()
    heading = serializers.CharField()
    items = FeatureItemSerializer(many=True)


class HowItWorksStepSerializer(serializers.Serializer):
    """How it works step serializer."""
    id = serializers.CharField(source='key')
    icon = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()


class HowItWorksSectionSerializer(serializers.Serializer):
    """How it works section serializer."""
    eyebrow = serializers.CharField()
    heading = serializers.CharField()
    steps = HowItWorksStepSerializer(many=True)


class GalleryPreviewPhotoSerializer(serializers.Serializer):
    """Gallery preview photo serializer."""
    id = serializers.CharField(source='key')
    url = serializers.URLField()
    alt = serializers.CharField(source='alt_text')
    aspect_ratio = serializers.CharField()


class GalleryPreviewSectionSerializer(serializers.Serializer):
    """Gallery preview section serializer."""
    eyebrow = serializers.CharField()
    heading = serializers.CharField()
    description = serializers.CharField()
    count_label = serializers.CharField()
    cta = CTASerializer()
    photos = GalleryPreviewPhotoSerializer(many=True)


class TestimonialSerializer(serializers.Serializer):
    """Testimonial item serializer."""
    id = serializers.CharField(source='key')
    quote = serializers.CharField()
    name = serializers.CharField()
    role = serializers.CharField()
    avatar = serializers.URLField(allow_null=True)


class TestimonialsSectionSerializer(serializers.Serializer):
    """Testimonials section serializer."""
    eyebrow = serializers.CharField()
    heading = serializers.CharField()
    items = TestimonialSerializer(many=True)


class CTABannerSectionSerializer(serializers.Serializer):
    """CTA banner section serializer."""
    heading = serializers.CharField()
    description = serializers.CharField()
    primary_cta = CTASerializer()
    secondary_cta = CTASerializer()


class HomepageSerializer(serializers.Serializer):
    """Complete homepage content serializer."""
    meta_title = serializers.CharField()
    meta_description = serializers.CharField()
    updated_at = serializers.DateTimeField()
    hero = HeroSectionSerializer()
    stats = StatItemSerializer(many=True)
    arena = ArenaSectionSerializer()
    features = FeaturesSectionSerializer()
    how_it_works = HowItWorksSectionSerializer()
    gallery_preview = GalleryPreviewSectionSerializer()
    testimonials = TestimonialsSectionSerializer()
    cta_banner = CTABannerSectionSerializer()


# ============================================================================
# Bookings Page Serializers
# ============================================================================


class BookingsBannerSerializer(serializers.Serializer):
    """Bookings banner serializer."""
    eyebrow = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    image = ImageSerializer()


class BookingsStepSerializer(serializers.Serializer):
    """Bookings step item serializer."""
    id = serializers.CharField(source='key')
    title = serializers.CharField()
    description = serializers.CharField()


class BookingsStepsSectionSerializer(serializers.Serializer):
    """Bookings steps section serializer."""
    heading = serializers.CharField()
    items = BookingsStepSerializer(many=True)


class BookingsRateRowSerializer(serializers.Serializer):
    """Rate row serializer."""
    id = serializers.CharField(source='key')
    title = serializers.CharField()
    hours = serializers.CharField()
    weekday_price = serializers.IntegerField()
    weekend_price = serializers.IntegerField()
    highlight = serializers.BooleanField()
    highlight_label = serializers.CharField(allow_blank=True)


class BookingsRatesEventSerializer(serializers.Serializer):
    """Events subsection serializer."""
    title = serializers.CharField()
    description = serializers.CharField()
    cta = CTASerializer()


class BookingsRatesSectionSerializer(serializers.Serializer):
    """Bookings rates section serializer."""
    heading = serializers.CharField()
    description = serializers.CharField()
    weekday_label = serializers.CharField()
    weekend_label = serializers.CharField()
    rows = BookingsRateRowSerializer(many=True)
    events = BookingsRatesEventSerializer()
    refreshments_note = serializers.CharField()


class BookingsPolicySerializer(serializers.Serializer):
    """Policy item serializer."""
    id = serializers.CharField(source='key')
    icon = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()


class BookingsPoliciesSectionSerializer(serializers.Serializer):
    """Bookings policies section serializer."""
    heading = serializers.CharField()
    items = BookingsPolicySerializer(many=True)


class BookingsHelpStripSerializer(serializers.Serializer):
    """Help strip serializer."""
    heading = serializers.CharField()
    description = serializers.CharField()
    cta = CTASerializer()


class BookingsPageSerializer(serializers.Serializer):
    """Complete bookings page content serializer."""
    meta_title = serializers.CharField()
    meta_description = serializers.CharField()
    updated_at = serializers.DateTimeField()
    banner = BookingsBannerSerializer()
    steps = BookingsStepsSectionSerializer()
    rates = BookingsRatesSectionSerializer()
    policies = BookingsPoliciesSectionSerializer()
    help_strip = BookingsHelpStripSerializer()



# ============================================================================
# Gallery Page Serializers
# ============================================================================


class GalleryHeaderSerializer(serializers.Serializer):
    """Gallery header serializer."""
    eyebrow = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()


class GalleryCategorySerializer(serializers.Serializer):
    """Gallery category serializer."""
    id = serializers.CharField(source='key')
    key = serializers.CharField()
    label = serializers.CharField()


class GalleryPhotoSerializer(serializers.Serializer):
    """Gallery photo serializer."""
    id = serializers.CharField(source='key')
    url = serializers.URLField()
    alt = serializers.CharField(source='alt_text')
    title = serializers.CharField()
    category = serializers.CharField()
    aspect_ratio = serializers.CharField()


class GalleryVideoSerializer(serializers.Serializer):
    """Gallery video serializer."""
    id = serializers.CharField(source='key')
    url = serializers.URLField()
    poster = serializers.URLField()
    title = serializers.CharField()
    category = serializers.CharField()
    duration_seconds = serializers.IntegerField()


class GalleryVideosSectionSerializer(serializers.Serializer):
    """Gallery videos section serializer."""
    heading = serializers.CharField()
    description = serializers.CharField()
    videos = GalleryVideoSerializer(many=True)


class GalleryCTASerializer(serializers.Serializer):
    """Gallery CTA serializer."""
    heading = serializers.CharField()
    description = serializers.CharField()
    button = CTASerializer()


class GalleryPageSerializer(serializers.Serializer):
    """Complete gallery page content serializer."""
    meta_title = serializers.CharField()
    meta_description = serializers.CharField()
    updated_at = serializers.DateTimeField()
    header = GalleryHeaderSerializer()
    categories = GalleryCategorySerializer(many=True)
    photos = GalleryPhotoSerializer(many=True)
    videos_section = GalleryVideosSectionSerializer()
    cta = GalleryCTASerializer()



# ============================================================================
# About Page Serializers
# ============================================================================


class AboutHeroSerializer(serializers.Serializer):
    """About hero section serializer."""
    eyebrow = serializers.CharField()
    title = serializers.CharField()
    title_highlight = serializers.CharField()
    description = serializers.CharField()
    image = ImageSerializer()


class AboutStatSerializer(serializers.Serializer):
    """About stat item serializer."""
    id = serializers.CharField(source='key')
    value = serializers.CharField()
    label = serializers.CharField()


class AboutMilestoneSerializer(serializers.Serializer):
    """About milestone item serializer."""
    id = serializers.CharField(source='key')
    year = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    image = ImageSerializer()


class AboutStorySerializer(serializers.Serializer):
    """About story section serializer."""
    eyebrow = serializers.CharField()
    heading = serializers.CharField()
    description = serializers.CharField()
    timeline_heading = serializers.CharField()
    timeline_hint = serializers.CharField()
    milestones = AboutMilestoneSerializer(many=True)


class AboutValueSerializer(serializers.Serializer):
    """About value item serializer."""
    id = serializers.CharField(source='key')
    icon = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()


class AboutValuesSerializer(serializers.Serializer):
    """About values section serializer."""
    eyebrow = serializers.CharField()
    heading = serializers.CharField()
    items = AboutValueSerializer(many=True)


class AboutCommunitySerializer(serializers.Serializer):
    """About community section serializer."""
    eyebrow = serializers.CharField()
    heading = serializers.CharField()
    description = serializers.CharField()
    bullets = serializers.ListField(child=serializers.CharField())
    image = ImageSerializer()


class AboutTeamMemberSerializer(serializers.Serializer):
    """About team member serializer."""
    id = serializers.CharField(source='key')
    full_name = serializers.CharField()
    role = serializers.CharField()
    profile_image = serializers.URLField(allow_null=True)


class AboutTeamSerializer(serializers.Serializer):
    """About team section serializer."""
    eyebrow = serializers.CharField()
    heading = serializers.CharField()
    description = serializers.CharField()
    members = AboutTeamMemberSerializer(many=True)


class AboutCTASerializer(serializers.Serializer):
    """About CTA banner serializer."""
    heading = serializers.CharField()
    description = serializers.CharField()
    primary_cta = CTASerializer()
    secondary_cta = CTASerializer()


class AboutPageSerializer(serializers.Serializer):
    """Complete about page content serializer."""
    meta_title = serializers.CharField()
    meta_description = serializers.CharField()
    updated_at = serializers.DateTimeField()
    hero = AboutHeroSerializer()
    stats = AboutStatSerializer(many=True)
    story = AboutStorySerializer()
    values = AboutValuesSerializer()
    community = AboutCommunitySerializer()
    team = AboutTeamSerializer()
    cta_banner = AboutCTASerializer()



# ============================================================================
# Contact Page Serializers
# ============================================================================


class ContactHeaderSerializer(serializers.Serializer):
    """Contact header section serializer."""
    eyebrow = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()


class ContactFormFieldSerializer(serializers.Serializer):
    """Contact form field serializer."""
    label = serializers.CharField()
    placeholder = serializers.CharField()


class ContactFormSuccessSerializer(serializers.Serializer):
    """Contact form success message serializer."""
    title = serializers.CharField()
    description = serializers.CharField()


class ContactFormSerializer(serializers.Serializer):
    """Contact form section serializer."""
    heading = serializers.CharField()
    description = serializers.CharField()
    submit_label = serializers.CharField()
    submitting_label = serializers.CharField()
    fields = serializers.DictField(child=ContactFormFieldSerializer())
    success = ContactFormSuccessSerializer()
    again_label = serializers.CharField()


class ContactDetailItemSerializer(serializers.Serializer):
    """Contact detail item serializer."""
    id = serializers.CharField(source='key')
    type = serializers.CharField(source='item_type')
    label = serializers.CharField()
    hint = serializers.CharField(allow_null=True)
    value_source = serializers.CharField()


class ContactDetailsSerializer(serializers.Serializer):
    """Contact details section serializer."""
    heading = serializers.CharField()
    description = serializers.CharField()
    maps_label = serializers.CharField()
    items = ContactDetailItemSerializer(many=True)


class ContactBookingCardSerializer(serializers.Serializer):
    """Contact booking card serializer."""
    title = serializers.CharField()
    description = serializers.CharField()
    cta = CTASerializer()


class ContactPageSerializer(serializers.Serializer):
    """Complete contact page content serializer."""
    meta_title = serializers.CharField()
    meta_description = serializers.CharField()
    updated_at = serializers.DateTimeField()
    header = ContactHeaderSerializer()
    form = ContactFormSerializer()
    details = ContactDetailsSerializer()
    booking_card = ContactBookingCardSerializer()


# ============================================================================
# Gallery Media Upload Serializers
# ============================================================================

class GalleryPhotoUploadSerializer(serializers.Serializer):
    """Serializer for uploading/updating gallery photos."""
    
    key = serializers.CharField(max_length=50, required=False)
    image = serializers.ImageField(required=False)
    alt_text = serializers.CharField(max_length=200)
    title = serializers.CharField(max_length=200)
    category = serializers.CharField(max_length=50)
    aspect_ratio = serializers.CharField(max_length=10, default="4/3")
    sort_order = serializers.IntegerField(default=0, min_value=0)
    is_active = serializers.BooleanField(default=True)
    
    def validate_category(self, value):
        """Validate category is one of the expected values."""
        valid_categories = ['ALL', 'VENUE', 'MATCHES', 'COMMUNITY']
        if value not in valid_categories:
            raise serializers.ValidationError(
                f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            )
        return value
    
    def validate_aspect_ratio(self, value):
        """Validate aspect ratio format."""
        valid_ratios = ['16/10', '16/9', '4/3', '1/1', '3/4']
        if value not in valid_ratios:
            raise serializers.ValidationError(
                f"Invalid aspect ratio. Must be one of: {', '.join(valid_ratios)}"
            )
        return value


class GalleryVideoUploadSerializer(serializers.Serializer):
    """Serializer for uploading/updating gallery videos."""
    
    key = serializers.CharField(max_length=50, required=False)
    video = serializers.FileField(required=False)
    poster = serializers.ImageField(required=False)
    title = serializers.CharField(max_length=200)
    category = serializers.CharField(max_length=50)
    duration_seconds = serializers.IntegerField(min_value=0)
    sort_order = serializers.IntegerField(default=0, min_value=0)
    is_active = serializers.BooleanField(default=True)
    
    def validate_category(self, value):
        """Validate category is one of the expected values."""
        valid_categories = ['ALL', 'VENUE', 'MATCHES', 'COMMUNITY']
        if value not in valid_categories:
            raise serializers.ValidationError(
                f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            )
        return value


class GalleryPhotoDetailSerializer(serializers.Serializer):
    """Detailed serializer for gallery photo responses."""
    
    id = serializers.UUIDField()
    key = serializers.CharField()
    image_url = serializers.SerializerMethodField()
    alt_text = serializers.CharField()
    title = serializers.CharField()
    category = serializers.CharField()
    aspect_ratio = serializers.CharField()
    sort_order = serializers.IntegerField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    
    def get_image_url(self, obj):
        """Get the full URL for the image."""
        return obj.image.url if obj.image else None


class GalleryVideoDetailSerializer(serializers.Serializer):
    """Detailed serializer for gallery video responses."""
    
    id = serializers.UUIDField()
    key = serializers.CharField()
    video_url = serializers.SerializerMethodField()
    poster_url = serializers.SerializerMethodField()
    title = serializers.CharField()
    category = serializers.CharField()
    duration_seconds = serializers.IntegerField()
    sort_order = serializers.IntegerField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    
    def get_video_url(self, obj):
        """Get the full URL for the video."""
        return obj.video.url if obj.video else None
    
    def get_poster_url(self, obj):
        """Get the full URL for the poster image."""
        return obj.poster.url if obj.poster else None
