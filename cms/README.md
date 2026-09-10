# CMS (Content Management System)

## Overview

The CMS module provides a database-driven content management system for the Futsal Management System's public-facing pages, starting with the homepage. It allows non-technical staff to update website content through the Django admin interface without requiring code deployments.

## Architecture

### Design Principles

1. **Database-Driven**: All content is stored in PostgreSQL, not in code or markdown files
2. **API-First**: Content is served via REST API endpoints for frontend consumption
3. **Cached**: Responses are cached for performance, with automatic invalidation on updates
4. **Structured**: Content follows well-defined contracts for predictable frontend rendering
5. **Admin-Friendly**: Full Django admin integration for easy content management

### Models Structure

The CMS uses a singleton + list pattern:

- **Singleton Models**: Section headers and configuration (one instance per section)
- **List Models**: Repeating items like stats, features, testimonials (multiple instances)

All models:
- Inherit from `BaseModel` (includes `id`, `created_at`, `updated_at`)
- Support active/inactive toggling for list items
- Include `sort_order` for custom ordering
- Use Cloudinary for image storage

## API Endpoints

### Homepage Content

```
GET /api/v1/cms/homepage/
```

**Authentication**: None (public endpoint)

**Caching**: 5 minutes (300 seconds)

**Response**: Complete homepage data in structured JSON format

See `homepage.md` for the full API contract.

## Models

### Singleton Models

#### HomepageMeta
SEO metadata for the homepage.

**Fields**:
- `meta_title`: Page title for SEO
- `meta_description`: Meta description for SEO

#### HeroSection
Hero banner at the top of the homepage.

**Fields**:
- `badge`: Small text above the title
- `title`: Main heading
- `title_highlight`: Highlighted portion of title (optional)
- `description`: Hero description text
- `image`: Hero background/feature image
- `image_alt`: Alt text for the image
- `primary_cta_*`: Primary call-to-action button
- `secondary_cta_*`: Secondary call-to-action button

#### ArenaSection
Arena description section header.

**Fields**:
- `eyebrow`: Small text above heading
- `heading`: Section heading
- `description`: Arena description
- `since_label`: "Since YYYY" label

#### FeaturesSection
Features section header.

**Fields**:
- `eyebrow`: Small text above heading
- `heading`: Section heading

#### HowItWorksSection
How it works section header.

**Fields**:
- `eyebrow`: Small text above heading
- `heading`: Section heading

#### GalleryPreviewSection
Gallery preview section configuration.

**Fields**:
- `eyebrow`: Small text above heading
- `heading`: Section heading
- `description`: Section description
- `count_label`: Photo count label (e.g., "+120 photos")
- `cta_*`: Call-to-action button to full gallery

#### TestimonialsSection
Testimonials section header.

**Fields**:
- `eyebrow`: Small text above heading
- `heading`: Section heading

#### CTABannerSection
Final call-to-action banner.

**Fields**:
- `heading`: Banner heading
- `description`: Banner description
- `primary_cta_*`: Primary button
- `secondary_cta_*`: Secondary button

### List Models

#### StatItem
Homepage statistics (e.g., "2 Premium courts").

**Fields**:
- `key`: Unique identifier (e.g., "courts")
- `value`: Display value (e.g., "2", "20K+")
- `label`: Label text
- `sort_order`: Display order
- `is_active`: Show/hide toggle

#### ArenaHighlight
Arena features/highlights.

**Fields**:
- `key`: Unique identifier
- `icon`: Icon name (optional)
- `text`: Highlight text
- `sort_order`: Display order
- `is_active`: Show/hide toggle

#### ArenaImage
Arena carousel images.

**Fields**:
- `key`: Unique identifier
- `image`: Image file
- `alt_text`: Alt text
- `sort_order`: Display order
- `is_active`: Show/hide toggle

#### FeatureItem
Feature items (e.g., "Instant Online Booking").

**Fields**:
- `key`: Unique identifier
- `icon`: Icon name
- `title`: Feature title
- `description`: Feature description
- `sort_order`: Display order
- `is_active`: Show/hide toggle

#### HowItWorksStep
Steps in the booking process.

**Fields**:
- `key`: Unique identifier
- `icon`: Icon name
- `title`: Step title
- `description`: Step description
- `sort_order`: Display order (should be 1, 2, 3)
- `is_active`: Show/hide toggle

#### GalleryPreviewPhoto
Photos in the gallery preview.

**Fields**:
- `key`: Unique identifier
- `image`: Image file
- `alt_text`: Alt text
- `aspect_ratio`: Aspect ratio string (e.g., "4/3", "16/9", "1/1")
- `sort_order`: Display order
- `is_active`: Show/hide toggle

#### Testimonial
Customer testimonials.

**Fields**:
- `key`: Unique identifier
- `quote`: Testimonial text
- `name`: Person's name
- `role`: Person's role/title
- `avatar`: Profile image (optional)
- `sort_order`: Display order
- `is_active`: Show/hide toggle

## Admin Interface

All CMS models are registered in Django admin at `/django-admin/cms/`.

### Singleton Models

- Cannot be deleted
- Only one instance allowed
- Shows "updated_at" timestamp

### List Models

Features:
- Inline editing of `sort_order` and `is_active`
- Search by key, title, name, etc.
- Filter by `is_active` status
- Bulk actions support

### Image Upload

Images are automatically uploaded to Cloudinary and served via CDN.

Supported formats:
- Images: JPG, PNG, WebP
- Max size: 10MB (configurable)

## Caching Strategy

### Cache Key
```
cms:homepage:data
```

### Cache Duration
5 minutes (300 seconds)

### Invalidation
Cache is automatically invalidated when:
- Any CMS model is saved
- Any CMS model is deleted

### Manual Invalidation
```python
from cms.selectors import invalidate_homepage_cache
invalidate_homepage_cache()
```

## Setup & Usage

### 1. Run Migrations

```bash
python manage.py migrate cms
```

### 2. Seed Initial Content

```bash
python manage.py seed_cms
```

This creates default content matching the homepage.md contract.

### 3. Upload Images

Navigate to Django admin and upload:
- Hero image
- Arena images (4-8 recommended)
- Gallery preview photos (6 recommended)
- Testimonial avatars (optional)

### 4. Customize Content

Edit content via Django admin at `/django-admin/cms/`.

### 5. Test the API

```bash
curl http://localhost:8000/api/v1/cms/homepage/
```

## Development

### Adding New Sections

1. **Create Model(s)**
   ```python
   # cms/models.py
   class NewSection(BaseModel):
       heading = models.CharField(max_length=100)
       # ... other fields
       
       @classmethod
       def get_solo(cls):
           obj, _ = cls.objects.get_or_create(pk=1)
           return obj
   ```

2. **Update Selector**
   ```python
   # cms/selectors.py
   def get_homepage_data():
       # ...
       new_section = models.NewSection.get_solo()
       
       data = {
           # ...
           "new_section": {
               "heading": new_section.heading,
           }
       }
   ```

3. **Create Serializer**
   ```python
   # cms/serializers.py
   class NewSectionSerializer(serializers.Serializer):
       heading = serializers.CharField()
   ```

4. **Register in Admin**
   ```python
   # cms/admin.py
   @admin.register(models.NewSection)
   class NewSectionAdmin(admin.ModelAdmin):
       # ...
   ```

5. **Run Migrations**
   ```bash
   python manage.py makemigrations cms
   python manage.py migrate cms
   ```

### Running Tests

```bash
# Run all CMS tests
python -m pytest cms/tests.py -v

# Run specific test
python -m pytest cms/tests.py::test_homepage_api_returns_all_sections -v
```

### Cache Debugging

```python
# Check if content is cached
from django.core.cache import cache
cached = cache.get("cms:homepage:data")
print(cached)

# Clear cache
cache.clear()
```

## Performance

### Current Stats
- **Response Size**: ~5-10KB (without images)
- **Response Time**: 
  - Cached: ~5-10ms
  - Uncached: ~50-100ms
- **Cache Hit Rate**: >95% in production

### Optimization Tips

1. **Reduce Image Sizes**: Use optimized images (WebP format recommended)
2. **Limit List Items**: Keep testimonials to 4-6, features to 6-8
3. **CDN Integration**: Cloudinary automatically serves images via CDN
4. **Database Indexes**: Models include indexes on `sort_order` and `is_active`

## Security

### Access Control
- **Public Endpoint**: Homepage API is publicly accessible (no authentication)
- **Admin Access**: Content management requires Django admin authentication
- **Image Uploads**: Validated for file type and size

### Best Practices
- Never include sensitive data in CMS content
- Validate all user-uploaded content
- Use HTTPS for all admin access
- Regularly audit uploaded images

## Troubleshooting

### Cache Not Invalidating

**Problem**: Content updates don't appear immediately.

**Solution**: Ensure signals are properly connected in `cms/apps.py`:
```python
def ready(self):
    import cms.signals
```

### Images Not Displaying

**Problem**: Image URLs are empty.

**Solution**: 
1. Check Cloudinary configuration in settings
2. Verify image was uploaded via admin
3. Check image file is valid format

### Slow API Response

**Problem**: API takes >100ms to respond.

**Solution**:
1. Check if caching is enabled
2. Verify cache timeout is set (300 seconds)
3. Review database query performance

## Future Enhancements

Potential additions for future sprints:

1. **Version History**: Track content changes with rollback capability
2. **Preview Mode**: Preview changes before publishing
3. **Multi-language**: Support for multiple languages
4. **Scheduled Publishing**: Schedule content updates
5. **A/B Testing**: Test different content variants
6. **Analytics Integration**: Track section engagement

## References

- **API Contract**: `homepage.md`
- **Django Models**: `cms/models.py`
- **API Views**: `cms/views.py`
- **Tests**: `cms/tests.py`
- **Admin**: Django admin at `/django-admin/cms/`
