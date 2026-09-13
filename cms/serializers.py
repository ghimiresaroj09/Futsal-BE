"""CMS serializers for testimonials."""
from __future__ import annotations

from rest_framework import serializers

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


class HeroSectionSerializer(serializers.ModelSerializer):
    """Serializer for hero section display."""
    
    image_url = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    
    class Meta:
        model = HeroSection
        fields = [
            "title_one",
            "title_two",
            "description",
            "image_url",
            "stats",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]
    
    def get_image_url(self, obj):
        """Get the full URL for the hero image."""
        if obj.image:
            return obj.image.url
        return None
    
    def get_stats(self, obj):
        """Return stats as a structured list."""
        return [
            {
                "label": obj.stat_open_label,
                "value": obj.stat_open_value
            },
            {
                "label": obj.stat_matches_label,
                "value": obj.stat_matches_value
            },
            {
                "label": obj.stat_courts_label,
                "value": obj.stat_courts_value
            }
        ]


class HeroSectionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating hero section."""
    
    # Mark stats as optional to bypass DRF's JSONField validation
    # We'll handle parsing and validation in the view
    stats = serializers.JSONField(required=False, allow_null=True)
    
    class Meta:
        model = HeroSection
        fields = [
            "title_one",
            "title_two",
            "description",
            "image",
            "stats",
        ]
        extra_kwargs = {
            'stats': {'required': False, 'allow_null': True},
        }
    
    def validate_title_one(self, value):
        """Validate title_one is not empty."""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Title one cannot be empty.")
        return value.strip() if value else value
    
    def validate_title_two(self, value):
        """Validate title_two is not empty."""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Title two cannot be empty.")
        return value.strip() if value else value


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for testimonial display (read-only)."""
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Testimonial
        fields = [
            "id",
            "full_name",
            "title",
            "image_url",
            "content",
            "is_active",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def get_image_url(self, obj):
        """Get the full URL for the image."""
        if obj.image:
            return obj.image.url
        return None


class TestimonialUploadSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating testimonials with image upload."""
    
    class Meta:
        model = Testimonial
        fields = [
            "full_name",
            "title",
            "image",
            "content",
            "is_active",
            "sort_order",
        ]
    
    def validate_full_name(self, value):
        """Validate full name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Full name cannot be empty.")
        return value.strip()
    
    def validate_content(self, value):
        """Validate content is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value.strip()



class CarouselImageSerializer(serializers.ModelSerializer):
    """Serializer for carousel image display."""
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CarouselImage
        fields = [
            "id",
            "image_url",
            "alt_text",
            "sort_order",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def get_image_url(self, obj):
        """Get the full URL for the carousel image."""
        if obj.image:
            return obj.image.url
        return None


class CarouselImageUploadSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating carousel images."""
    
    class Meta:
        model = CarouselImage
        fields = [
            "image",
            "alt_text",
            "sort_order",
            "is_active",
        ]
    
    def validate_alt_text(self, value):
        """Validate alt text is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Alt text cannot be empty.")
        return value.strip()



class ArenaSectionSerializer(serializers.ModelSerializer):
    """Serializer for arena section display."""
    
    class Meta:
        model = ArenaSection
        fields = [
            "title",
            "description",
            "features",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]


class ArenaSectionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating arena section."""
    
    # Mark features as optional to bypass DRF's JSONField validation
    # We'll handle parsing and validation in the view
    features = serializers.JSONField(required=False, allow_null=True)
    
    class Meta:
        model = ArenaSection
        fields = [
            "title",
            "description",
            "features",
        ]
        extra_kwargs = {
            'features': {'required': False, 'allow_null': True},
        }
    
    def validate_title(self, value):
        """Validate title is not empty."""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip() if value else value



class WhyUsSectionSerializer(serializers.ModelSerializer):
    """Serializer for why us section display."""
    
    class Meta:
        model = WhyUsSection
        fields = [
            "title",
            "description",
            "features",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]


class WhyUsSectionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating why us section."""
    
    # Mark features as optional to bypass DRF's JSONField validation
    # We'll handle parsing and validation in the view
    features = serializers.JSONField(required=False, allow_null=True)
    
    class Meta:
        model = WhyUsSection
        fields = [
            "title",
            "description",
            "features",
        ]
        extra_kwargs = {
            'features': {'required': False, 'allow_null': True},
        }
    
    def validate_title(self, value):
        """Validate title is not empty."""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip() if value else value



class GalleryCategorySerializer(serializers.ModelSerializer):
    """Serializer for gallery category display."""
    
    class Meta:
        model = GalleryCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "is_active",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "slug"]


class GalleryCategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating gallery categories."""
    
    class Meta:
        model = GalleryCategory
        fields = [
            "name",
            "description",
            "is_active",
            "sort_order",
        ]
    
    def validate_name(self, value):
        """Validate name is not empty and handle uniqueness."""
        if not value or not value.strip():
            raise serializers.ValidationError("Category name cannot be empty.")
        
        value = value.strip()
        
        # Check uniqueness (case-insensitive)
        instance_id = self.instance.id if self.instance else None
        if GalleryCategory.objects.filter(
            name__iexact=value
        ).exclude(id=instance_id).exists():
            raise serializers.ValidationError(
                f"A category with name '{value}' already exists."
            )
        
        return value
    
    def validate_sort_order(self, value):
        """Validate sort order is not negative."""
        if value < 0:
            raise serializers.ValidationError("Sort order cannot be negative.")
        return value
    
    def save(self, **kwargs):
        """Override save to regenerate slug when name changes."""
        from django.utils.text import slugify
        
        # If updating and name has changed, regenerate slug
        if self.instance and 'name' in self.validated_data:
            new_name = self.validated_data['name']
            if new_name != self.instance.name:
                # Generate slug from new name
                base_slug = slugify(new_name)
                slug = base_slug
                counter = 1
                
                # Ensure slug is unique
                while GalleryCategory.objects.filter(slug=slug).exclude(id=self.instance.id).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                
                self.validated_data['slug'] = slug
        
        return super().save(**kwargs)



class GalleryImageSerializer(serializers.ModelSerializer):
    """Serializer for gallery image display."""
    
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    
    class Meta:
        model = GalleryImage
        fields = [
            "id",
            "title",
            "image_url",
            "alt_text",
            "category",
            "category_name",
            "category_slug",
            "is_active",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def get_image_url(self, obj):
        """Get the full URL for the image."""
        if obj.image:
            return obj.image.url
        return None


class GalleryImageUploadSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating gallery images."""
    
    class Meta:
        model = GalleryImage
        fields = [
            "title",
            "image",
            "alt_text",
            "category",
            "is_active",
            "sort_order",
        ]
    
    def validate_title(self, value):
        """Validate title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip()
    
    def validate_alt_text(self, value):
        """Validate alt text is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Alt text cannot be empty.")
        return value.strip()
    
    def validate_category(self, value):
        """Validate category exists and is active."""
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot add images to an inactive category."
            )
        return value
    
    def validate_sort_order(self, value):
        """Validate sort order is not negative."""
        if value < 0:
            raise serializers.ValidationError("Sort order cannot be negative.")
        return value



class GalleryHighlightSerializer(serializers.ModelSerializer):
    """Serializer for gallery highlight display."""
    
    video_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = GalleryHighlight
        fields = [
            "id",
            "title",
            "video_url",
            "thumbnail_url",
            "tags",
            "is_active",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def get_video_url(self, obj):
        """Get the full URL for the video."""
        if obj.video:
            return obj.video.url
        return None
    
    def get_thumbnail_url(self, obj):
        """Get the full URL for the thumbnail."""
        if obj.thumbnail:
            return obj.thumbnail.url
        return None


class GalleryHighlightUploadSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating gallery highlights."""
    
    class Meta:
        model = GalleryHighlight
        fields = [
            "title",
            "video",
            "thumbnail",
            "tags",
            "is_active",
            "sort_order",
        ]
    
    def validate_title(self, value):
        """Validate title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip()
    
    def validate_tags(self, value):
        """Validate and clean tags."""
        if value:
            return value.strip()
        return ""
    
    def validate_sort_order(self, value):
        """Validate sort order is not negative."""
        if value < 0:
            raise serializers.ValidationError("Sort order cannot be negative.")
        return value


class AboutHeroSectionSerializer(serializers.ModelSerializer):
    """Serializer for about hero section display."""
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = AboutHeroSection
        fields = [
            "title",
            "description",
            "image_url",
            "years_in_game",
            "matches_hosted",
            "tournaments_run",
            "players_in_community",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]
    
    def get_image_url(self, obj):
        """Get the full URL for the hero image."""
        if obj.image:
            return obj.image.url
        return None


class AboutHeroSectionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating about hero section."""
    
    class Meta:
        model = AboutHeroSection
        fields = [
            "title",
            "description",
            "image",
            "years_in_game",
            "matches_hosted",
            "tournaments_run",
            "players_in_community",
        ]
    
    def validate_title(self, value):
        """Validate title is not empty."""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip() if value else value


class AboutStorySerializer(serializers.ModelSerializer):
    """Serializer for about story section display."""
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = AboutStory
        fields = [
            "title",
            "description",
            "image_url",
            "journey",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]
    
    def get_image_url(self, obj):
        """Get the full URL for the story image."""
        if obj.image:
            return obj.image.url
        return None


class AboutStoryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating about story section."""
    
    class Meta:
        model = AboutStory
        fields = [
            "title",
            "description",
            "image",
            "journey",
        ]
        # Skip validation for JSON fields - view handles them
        extra_kwargs = {
            'journey': {'required': False, 'allow_null': True},
        }
    
    def validate_title(self, value):
        """Validate title is not empty."""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip() if value else value


class AboutCommunitySerializer(serializers.ModelSerializer):
    """Serializer for about community section display."""
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = AboutCommunity
        fields = [
            "title",
            "description",
            "image_url",
            "features",
            "team",
            "rules",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]
    
    def get_image_url(self, obj):
        """Get the full URL for the community image."""
        if obj.image:
            return obj.image.url
        return None


class AboutCommunityUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating about community section."""
    
    class Meta:
        model = AboutCommunity
        fields = [
            "title",
            "description",
            "image",
            "features",
            "team",
            "rules",
        ]
        # Skip validation for JSON fields - view handles them
        extra_kwargs = {
            'features': {'required': False, 'allow_null': True},
            'team': {'required': False, 'allow_null': True},
            'rules': {'required': False, 'allow_null': True},
        }
    
    def validate_title(self, value):
        """Validate title is not empty."""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip() if value else value


class BookingsHeroSectionSerializer(serializers.ModelSerializer):
    """Serializer for bookings hero section display."""
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = BookingsHeroSection
        fields = [
            "title",
            "description",
            "image_url",
            "info",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]
    
    def get_image_url(self, obj):
        """Get the full URL for the hero image."""
        if obj.image:
            return obj.image.url
        return None


class BookingsHeroSectionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating bookings hero section."""
    
    class Meta:
        model = BookingsHeroSection
        fields = [
            "title",
            "description",
            "image",
            "info",
        ]
    
    def validate_title(self, value):
        """Validate title is not empty."""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value.strip() if value else value
    
    def validate_info(self, value):
        """Validate info is an array of objects with iconcode, title, and description."""
        if value is not None:
            if not isinstance(value, list):
                raise serializers.ValidationError("Info must be an array.")
            
            for idx, item in enumerate(value):
                if not isinstance(item, dict):
                    raise serializers.ValidationError(
                        f"Info item at index {idx} must be an object."
                    )
                
                # Check required fields
                required_fields = ["iconcode", "title", "description"]
                for field in required_fields:
                    if field not in item:
                        raise serializers.ValidationError(
                            f"Info item at index {idx} is missing required field: '{field}'."
                        )
                    
                    if not isinstance(item[field], str):
                        raise serializers.ValidationError(
                            f"Info item at index {idx}: '{field}' must be a string."
                        )
                    
                    if not item[field].strip():
                        raise serializers.ValidationError(
                            f"Info item at index {idx}: '{field}' cannot be empty."
                        )
        
        return value


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQ display and management."""

    class Meta:
        model = FAQ
        fields = ["id", "question", "answer", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_question(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Question cannot be empty.")
        return value.strip()

    def validate_answer(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Answer cannot be empty.")
        return value.strip()


class TermsAndPrivacySerializer(serializers.ModelSerializer):
    """Serializer for terms and privacy policy content."""

    class Meta:
        model = TermsAndPrivacy
        fields = ["terms", "privacy", "updated_at"]
        read_only_fields = ["updated_at"]
