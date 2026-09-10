# Media Management Analysis & Integration Strategy

## Current State 📊

### Existing Media API (`/api/v1/admin/media/`)

**Purpose**: Manages Futsal venue gallery (general futsal photos/videos)

**Model**: `FutsalMedia`
```python
- futsal (FK to Futsal)
- media_type (IMAGE/VIDEO)
- image (Cloudinary)
- video (Cloudinary)
- caption
- is_cover (boolean)
- sort_order
- uploaded_by
```

**Endpoints**:
```
GET    /api/v1/admin/media/           - List all futsal media
POST   /api/v1/admin/media/           - Upload image/video
GET    /api/v1/admin/media/{id}/      - Get media details
PUT    /api/v1/admin/media/{id}/      - Update metadata
PATCH  /api/v1/admin/media/{id}/      - Partial update
DELETE /api/v1/admin/media/{id}/      - Delete media
```

**Features**:
- ✅ Multipart file upload support
- ✅ Cloudinary integration
- ✅ Admin-only permissions
- ✅ Sort order management
- ✅ Cover photo flag
- ✅ Automatic file deletion on delete
- ✅ Filter by media_type, is_cover
- ✅ Order by sort_order, created_at

### CMS Gallery Models

**Purpose**: CMS-managed gallery page content

**Models**: `GalleryPhoto`, `GalleryVideo`
```python
GalleryPhoto:
- key (unique)
- image (Cloudinary)
- alt_text
- title
- category (VENUE/MATCHES/COMMUNITY)
- aspect_ratio
- sort_order
- is_active

GalleryVideo:
- key (unique)
- video (Cloudinary)
- poster (thumbnail image)
- title
- category
- duration_seconds
- sort_order
- is_active
```

**Current Status**:
- ✅ GET endpoint works
- ✅ PATCH endpoint for text fields only
- ❌ No file upload capability via API

## Where Each is Used 🎯

### 1. FutsalMedia (`/api/v1/admin/media/`)

**Used in:**

#### A. Futsal Info Endpoint (`GET /api/v1/futsal/`)
```json
{
  "id": "...",
  "name": "Nexus Futsal",
  "description": "...",
  "media": [
    {
      "id": "...",
      "media_type": "IMAGE",
      "url": "https://cloudinary.com/...",
      "caption": "Indoor court view",
      "is_cover": true,
      "sort_order": 1
    }
  ]
}
```

**Purpose**: Display venue photos/videos on venue info pages, hero sections, about page venue showcase

#### B. Homepage CMS (Potential)
- Arena section images
- Hero background images
- Venue showcase sections

**Context**: General venue photos for marketing and information

### 2. CMS Gallery (`/api/v1/cms/gallery/`)

**Used in:**

#### A. Gallery Page (`/gallery`)
Dedicated photo/video gallery page with:
- Category filtering (ALL/VENUE/MATCHES/COMMUNITY)
- Masonry grid layout
- Lightbox viewing
- Video player

**Purpose**: Curated gallery experience with categorization

**Context**: Marketing/promotional content, organized by purpose

## Key Differences 🔄

| Feature | FutsalMedia | CMS Gallery |
|---------|-------------|-------------|
| **Purpose** | Venue info gallery | CMS gallery page |
| **Categories** | None (general) | VENUE/MATCHES/COMMUNITY |
| **Display** | Futsal info endpoint | Gallery page only |
| **Management** | Admin media API | CMS (currently admin panel) |
| **Cover Photo** | Yes (is_cover flag) | No |
| **Aspect Ratio** | Not specified | Configurable |
| **Poster/Thumbnail** | No | Yes (for videos) |
| **Duration** | No | Yes (for videos) |
| **Alt Text** | Caption only | Full alt text for accessibility |

## Recommended Integration Strategy 🎯

### Option 1: Dual System (Current + Enhanced) ⭐ RECOMMENDED

**Keep both systems with clear separation:**

#### FutsalMedia API
**Purpose**: General venue photos/videos for info pages
**Usage**: Homepage, About page, Futsal info
**Keep as-is**: `/api/v1/admin/media/`

#### Enhanced CMS Gallery API
**Purpose**: Curated gallery page with categories
**Usage**: Gallery page only
**Create new endpoints**:

```
# Gallery Photos
GET    /api/v1/cms/gallery/photos/
POST   /api/v1/cms/gallery/photos/
PATCH  /api/v1/cms/gallery/photos/{id}/
DELETE /api/v1/cms/gallery/photos/{id}/

# Gallery Videos
GET    /api/v1/cms/gallery/videos/
POST   /api/v1/cms/gallery/videos/
PATCH  /api/v1/cms/gallery/videos/{id}/
DELETE /api/v1/cms/gallery/videos/{id}/
```

**Benefits**:
✅ Clear separation of concerns
✅ Gallery photos have categories (FutsalMedia doesn't)
✅ Different display requirements (aspect ratio, alt text)
✅ Gallery videos have posters and duration
✅ Can sync/copy between systems if needed
✅ No breaking changes to existing FutsalMedia usage

### Option 2: Unified System (Complex)

**Merge both into one system:**
- Add categories to FutsalMedia
- Add aspect_ratio, alt_text fields
- Add poster and duration for videos
- Update all consuming endpoints

**Drawbacks**:
❌ Breaking changes to FutsalMedia consumers
❌ Mixed purposes in one model
❌ More complex queries
❌ Harder to maintain separation

### Option 3: Reuse FutsalMedia for Gallery

**Use existing FutsalMedia API for gallery page:**
- Add category field to FutsalMedia
- Filter by category for gallery page

**Drawbacks**:
❌ Missing gallery-specific fields (aspect_ratio, alt_text, poster)
❌ is_cover flag doesn't fit gallery use case
❌ Caption vs. title + alt_text confusion
❌ No video duration or poster

## Recommended Implementation 📝

### Phase 1: Create CMS Gallery Media API

**New ViewSets:**

```python
# cms/views.py

class GalleryPhotoViewSet(viewsets.ModelViewSet):
    """Manage CMS gallery photos."""
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = GalleryPhoto.objects.all()
    filterset_fields = ["category", "is_active"]
    ordering_fields = ["sort_order", "created_at"]
    
    def create(self, request):
        # Upload photo to Cloudinary
        # Save metadata
        # Return photo data
    
    def destroy(self, request, pk):
        # Delete from Cloudinary
        # Delete from database

class GalleryVideoViewSet(viewsets.ModelViewSet):
    """Manage CMS gallery videos."""
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = GalleryVideo.objects.all()
    filterset_fields = ["category", "is_active"]
    ordering_fields = ["sort_order", "created_at"]
    
    def create(self, request):
        # Upload video to Cloudinary
        # Upload poster image
        # Save metadata
        # Return video data
```

**New URLs:**

```python
# cms/urls.py
from rest_framework.routers import DefaultRouter

gallery_router = DefaultRouter()
gallery_router.register(r'gallery/photos', GalleryPhotoViewSet, basename='cms-gallery-photos')
gallery_router.register(r'gallery/videos', GalleryVideoViewSet, basename='cms-gallery-videos')

urlpatterns = [
    # Existing page endpoints
    path("homepage/", HomepageView.as_view(), name="cms-homepage"),
    path("bookings/", BookingsPageView.as_view(), name="cms-bookings"),
    path("gallery/", GalleryPageView.as_view(), name="cms-gallery"),
    path("about/", AboutPageView.as_view(), name="cms-about"),
    path("contact/", ContactPageView.as_view(), name="cms-contact"),
]

# Add router URLs
urlpatterns += gallery_router.urls
```

### Phase 2: Frontend Integration

**Admin CMS Gallery UI:**

```typescript
// Gallery Photo Management
async function uploadPhoto(file, metadata) {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('title', metadata.title);
  formData.append('alt_text', metadata.alt_text);
  formData.append('category', metadata.category);
  formData.append('aspect_ratio', metadata.aspect_ratio);
  
  const response = await fetch('/api/v1/cms/gallery/photos/', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });
  
  return response.json();
}

// List photos
async function getGalleryPhotos(category = null) {
  const url = category 
    ? `/api/v1/cms/gallery/photos/?category=${category}`
    : '/api/v1/cms/gallery/photos/';
    
  const response = await fetch(url);
  return response.json();
}

// Delete photo
async function deletePhoto(id) {
  await fetch(`/api/v1/cms/gallery/photos/${id}/`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
}
```

### Phase 3: Optional - Sync Utility

**Create admin action to copy FutsalMedia → CMS Gallery:**

```python
# Management command
python manage.py sync_media_to_gallery

# Copies selected FutsalMedia items to CMS Gallery
# Useful for initial population
```

## Summary & Recommendation 💡

### What to Do:

**1. Keep FutsalMedia API as-is**
- Used for: Venue info, homepage, general marketing
- Don't change it - working well

**2. Create new CMS Gallery Media API**
- New endpoints for gallery photos/videos
- Separate from FutsalMedia
- Category-based (VENUE/MATCHES/COMMUNITY)
- Full metadata (title, alt_text, aspect_ratio, poster, duration)

**3. Clear Separation:**
```
FutsalMedia          → General venue photos/videos
CMS Gallery Photos   → Categorized gallery page photos
CMS Gallery Videos   → Categorized gallery page videos (with posters)
```

### Benefits:

✅ **No breaking changes** to existing FutsalMedia usage
✅ **Purpose-built** - Each system for its specific use case
✅ **Better UX** - Gallery has categories, aspect ratios, better metadata
✅ **Flexibility** - Can evolve independently
✅ **Clarity** - Clear which API to use for what

### Migration Path:

1. **Now**: Create CMS Gallery Media API (photos + videos)
2. **Frontend**: Build admin UI for uploading gallery media
3. **Optional**: Create sync utility to copy FutsalMedia → Gallery
4. **Future**: Consider adding "use in gallery" checkbox to FutsalMedia upload

---

**Should I proceed with implementing the CMS Gallery Media API (Option 1)?**

This will give you:
- Full CRUD API for gallery photos
- Full CRUD API for gallery videos  
- Multipart upload support
- Category management
- Cloudinary integration
- No impact on existing FutsalMedia functionality

Let me know and I'll implement it! 🚀
