# CMS Quick Start Guide

## For Developers

### Initial Setup

```bash
# 1. Migrations are already run, but if needed:
python manage.py migrate cms

# 2. Seed default content
python manage.py seed_cms

# 3. Start development server (if not running)
python manage.py runserver

# 4. Test the API
curl http://localhost:8000/api/v1/cms/homepage/
```

### Running Tests

```bash
# All CMS tests
python -m pytest cms/tests.py -v

# Specific test
python -m pytest cms/tests.py::test_homepage_api_returns_all_sections -v
```

### Clear Cache

```python
from django.core.cache import cache
cache.clear()
```

## For Content Managers

### Access Admin

1. Navigate to: `http://localhost:8000/django-admin/`
2. Login with admin credentials
3. Go to **CMS** section

### Update Homepage Sections

#### SEO Metadata
1. Go to **Homepage Meta**
2. Edit `meta_title` and `meta_description`
3. Click **Save**

#### Hero Section
1. Go to **Hero Sections**
2. Edit title, description, image
3. Update CTA button labels and links
4. Click **Save**

#### Statistics
1. Go to **Stat Items**
2. Add/Edit/Delete stats
3. Adjust **sort_order** for positioning
4. Toggle **is_active** to show/hide
5. Click **Save**

#### Features
1. Go to **Feature Items**
2. Add/Edit/Delete features
3. Set icon name (e.g., "zap", "clock")
4. Adjust **sort_order**
5. Click **Save**

#### Testimonials
1. Go to **Testimonials**
2. Add/Edit/Delete testimonials
3. Upload avatar images (optional)
4. Adjust **sort_order**
5. Click **Save**

### Upload Images

1. Navigate to the relevant section (Hero, Arena Images, Gallery Photos)
2. Click **Add** or **Edit**
3. Click **Choose File** under image field
4. Select image (JPG, PNG, WebP - max 10MB)
5. Add alt text
6. Click **Save**

Images are automatically uploaded to Cloudinary.

## API Endpoints

### Homepage Content

```http
GET /api/v1/cms/homepage/
```

**Response**: Complete homepage data with all sections

**Caching**: Yes (5 minutes)

**Authentication**: None (public)

## Common Tasks

### Reorder Items

1. Go to the list view (e.g., Features, Testimonials)
2. Edit the **sort_order** field directly in the list
3. Items with lower numbers appear first
4. Click **Save**

### Hide/Show Items

1. Go to the list view
2. Toggle the **is_active** checkbox
3. Inactive items don't appear in the API
4. Click **Save**

### Update Call-to-Action Buttons

CTAs are in:
- Hero Section (primary & secondary)
- Gallery Preview Section
- CTA Banner Section (primary & secondary)

Fields:
- `*_cta_label`: Button text
- `*_cta_href`: Link URL (e.g., `/bookings`)
- `*_cta_style`: Button style ("primary", "secondary", "outline")

## Troubleshooting

### Content Not Updating

**Issue**: Made changes but not seeing them on frontend

**Solution**: 
1. Cache takes 5 minutes to refresh
2. Hard refresh browser (Ctrl+F5)
3. Or clear server cache:
   ```python
   from cms.selectors import invalidate_homepage_cache
   invalidate_homepage_cache()
   ```

### Images Not Showing

**Issue**: Image URLs are empty

**Solution**:
1. Check if image was actually uploaded
2. Verify Cloudinary configuration
3. Check image file format (JPG, PNG, WebP)
4. Check file size (<10MB)

### Wrong Item Order

**Issue**: Items appearing in wrong order

**Solution**:
1. Check `sort_order` field
2. Lower numbers appear first
3. Set to 1, 2, 3, etc.

## Best Practices

### Content Guidelines

1. **SEO**: Keep meta_title under 60 characters, meta_description under 160
2. **Headings**: Use sentence case, keep concise
3. **Descriptions**: Clear, benefit-focused, action-oriented
4. **Images**: Use WebP format, optimize before upload
5. **Alt Text**: Descriptive, include context
6. **CTAs**: Use action verbs ("Book a Slot", not "Click Here")

### Item Limits

Recommended item counts for best UX:
- **Stats**: Exactly 3
- **Arena Highlights**: 4-8 items
- **Arena Images**: 4-8 images
- **Features**: 6 items (fits grid perfectly)
- **How It Works Steps**: Exactly 3
- **Gallery Preview**: 6 photos
- **Testimonials**: 4-6 items

### Icons

Common icon names (Lucide icons):
- `zap` - Lightning bolt
- `clock` - Clock
- `calendar-check` - Calendar with check
- `trophy` - Trophy
- `shield-check` - Shield with check
- `sparkles` - Sparkles
- `map-pin` - Location pin
- `wifi` - WiFi
- `dumbbell` - Dumbbell
- `briefcase` - Briefcase
- `footprints` - Footprints

## File Locations

```
cms/
├── models.py          # Data models
├── admin.py           # Admin interface
├── views.py           # API endpoints
├── tests.py           # Test suite
├── README.md          # Full documentation
└── QUICKSTART.md      # This file
```

## Need Help?

- **Full Documentation**: See `cms/README.md`
- **API Contract**: See `homepage.md`
- **Tests**: Check `cms/tests.py` for usage examples

## Quick Reference

| Task | Admin Section | Key Fields |
|------|---------------|------------|
| Update page title | Homepage Meta | meta_title, meta_description |
| Change hero image | Hero Sections | image, image_alt |
| Edit stats | Stat Items | value, label, sort_order |
| Manage features | Feature Items | title, description, icon |
| Update testimonials | Testimonials | quote, name, role, avatar |
| Configure CTA | Hero/CTA Banner | *_cta_label, *_cta_href |

---

**Last Updated**: September 10, 2026  
**Version**: 1.0
