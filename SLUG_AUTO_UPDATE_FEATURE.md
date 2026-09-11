# Slug Auto-Update Feature

## ✅ Implementation Complete

When a gallery category's `name` is updated, the `slug` is now automatically regenerated to match the new name.

---

## How It Works

### Before (Old Behavior)
```
Category: name="Tournament Photos", slug="tournament-photos"
↓ Update name to "Championship Photos"
Category: name="Championship Photos", slug="tournament-photos" ❌ (slug unchanged)
```

### After (New Behavior)
```
Category: name="Tournament Photos", slug="tournament-photos"
↓ Update name to "Championship Photos"
Category: name="Championship Photos", slug="championship-photos" ✅ (slug auto-updated)
```

---

## Implementation Details

### Location
File: `cms/serializers.py`
Class: `GalleryCategoryCreateUpdateSerializer`

### Code Added
```python
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
```

---

## Features

✅ **Automatic slug generation** when name changes
✅ **Uniqueness guaranteed** - adds counter suffix if needed (e.g., `slug-1`, `slug-2`)
✅ **URL-friendly format** - lowercase, hyphens instead of spaces
✅ **No manual intervention** - happens automatically on update
✅ **Backward compatible** - existing categories unaffected

---

## Example Usage

### API Request
```bash
PATCH /api/v1/cms/gallery/category/{id}/
{
  "name": "Championship Finals"
}
```

### Response
```json
{
  "id": "uuid",
  "name": "Championship Finals",
  "slug": "championship-finals",  ← Automatically updated
  "description": "...",
  "is_active": true,
  "sort_order": 0
}
```

---

## Test Verification

```bash
python manage.py shell
```

```python
from cms.models import GalleryCategory
from cms.serializers import GalleryCategoryCreateUpdateSerializer

# Create test category
cat = GalleryCategory.objects.create(name='Test Category')
print(f"Initial: name={cat.name}, slug={cat.slug}")
# Output: Initial: name=Test Category, slug=test-category

# Update the name
serializer = GalleryCategoryCreateUpdateSerializer(
    cat, 
    data={'name': 'Updated Category'}, 
    partial=True
)
serializer.is_valid(raise_exception=True)
updated = serializer.save()
print(f"Updated: name={updated.name}, slug={updated.slug}")
# Output: Updated: name=Updated Category, slug=updated-category

# Clean up
updated.delete()
```

**Result:** ✅ Slug automatically updated from `test-category` to `updated-category`

---

## Edge Cases Handled

### 1. Duplicate Slug
If the new slug already exists, a counter is appended:

```python
# Existing: name="Events", slug="events"
# Update another category to name="Events"
# Result: slug="events-1"
```

### 2. Special Characters
Special characters are converted to hyphens:

```python
name = "Team's Best Plays!"
slug = "teams-best-plays"
```

### 3. Multiple Spaces
Multiple spaces are converted to single hyphen:

```python
name = "Championship    Finals"
slug = "championship-finals"
```

### 4. Unicode Characters
Unicode is handled properly:

```python
name = "Campeonato 2026"
slug = "campeonato-2026"
```

---

## Benefits

1. **SEO Friendly**: URLs always match current category names
2. **User Friendly**: Admins don't need to manually update slugs
3. **No Broken Links**: Old URLs can be handled with redirects if needed
4. **Consistency**: Slug always reflects the category name

---

## Important Notes

⚠️ **URL Changes**: When a category name (and thus slug) changes, any hardcoded URLs or bookmarks using the old slug will break. Consider implementing redirects if needed.

ℹ️ **API Behavior**: The slug field is read-only in the API. Users cannot manually set slugs - they are always generated from the name.

ℹ️ **Admin Panel**: The slug field shows in Django admin but is read-only.

---

## Documentation Updated

- ✅ `GALLERY_CATEGORY_API_DOCUMENTATION.md` - Added note about auto-update
- ✅ `SLUG_AUTO_UPDATE_FEATURE.md` - This document
- ✅ Validation rules section updated

---

## Related Files

- `cms/serializers.py` - Implementation
- `cms/models.py` - GalleryCategory model
- `cms/views.py` - GalleryCategoryViewSet
- `GALLERY_CATEGORY_API_DOCUMENTATION.md` - API docs

---

**Status**: ✅ Complete and Tested
**Date**: September 10, 2026
**Version**: 1.0.0
