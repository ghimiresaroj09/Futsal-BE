# Gallery Highlights API Documentation

## Overview
The Gallery Highlights API allows you to manage video highlights for the futsal arena. Videos are stored on Cloudinary with support for thumbnails and tags. This is the 9th CMS component.

**Base URL**: `/api/v1/cms/gallery/highlights/`

**Authentication**: 
- Public: Read access (GET - list and detail)
- Admin: Full CRUD access

---

## Model Schema

### GalleryHighlight
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | Auto | Unique identifier |
| `title` | String | Yes | Video title (max 200 chars) |
| `video` | File | Yes | Video file (uploaded to Cloudinary at `highlights/`) |
| `thumbnail` | Image | No | Optional video thumbnail (uploaded to `highlights/thumbnails/`) |
| `tags` | String | No | Tags as text (e.g., "goal, save, skills") |
| `is_active` | Boolean | No | Show on website (default: `true`) |
| `sort_order` | Integer | No | Display order (default: `0`, non-negative) |
| `created_at` | DateTime | Auto | Creation timestamp |
| `updated_at` | DateTime | Auto | Last update timestamp |

---

## Endpoints

### 1. List All Gallery Highlights
**GET** `/api/v1/cms/gallery/highlights/`

Returns all active highlights. Admins see all highlights including inactive ones.

**Query Parameters:**
- `is_active` (boolean): Filter by active status
- `search` (string): Search in title and tags
- `ordering` (string): Sort by `sort_order`, `title`, or `created_at`
- `page` (integer): Page number for pagination
- `page_size` (integer): Items per page

**Response:** `200 OK`
```json
{
  "status": "success",
  "message": "Data retrieved successfully",
  "data": {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Amazing Goal Compilation",
        "video_url": "https://res.cloudinary.com/.../highlights/video.mp4",
        "thumbnail_url": "https://res.cloudinary.com/.../highlights/thumbnails/thumb.jpg",
        "tags": "goal, skills, tournament",
        "is_active": true,
        "sort_order": 0,
        "created_at": "2026-09-10T10:30:00Z",
        "updated_at": "2026-09-10T10:30:00Z"
      }
    ]
  }
}
```

**Ordering Examples:**
- `?ordering=sort_order` - Lowest sort_order first
- `?ordering=-created_at` - Newest first (default within same sort_order)
- `?ordering=title` - Alphabetical by title

---

### 2. Upload Gallery Highlight
**POST** `/api/v1/cms/gallery/highlights/`

Upload a new highlight video. **Admin only**.

**Request:** `multipart/form-data`
```
title: Amazing Goal Compilation
video: [video file]
thumbnail: [image file] (optional)
tags: goal, highlight, tournament
is_active: true
sort_order: 0
```

**Example in Swagger UI**:
```
tags: goal, highlight, tournament
```

**Response:** `201 Created`
```json
{
  "status": "success",
  "message": "Gallery highlight uploaded successfully.",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Amazing Goal Compilation",
    "video_url": "https://res.cloudinary.com/.../highlights/video.mp4",
    "thumbnail_url": "https://res.cloudinary.com/.../highlights/thumbnails/thumb.jpg",
    "tags": "goal, skills, tournament",
    "is_active": true,
    "sort_order": 0,
    "created_at": "2026-09-10T10:30:00Z",
    "updated_at": "2026-09-10T10:30:00Z"
  }
}
```

**Validation Rules:**
- `title`: Cannot be empty
- `video`: Required on creation
- `tags`: Plain text string, can be empty
- `sort_order`: Cannot be negative

**Error Response:** `400 Bad Request`
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "title": ["Title cannot be empty."],
    "sort_order": ["Sort order cannot be negative."]
  }
}
```

---

### 3. Get Highlight Detail
**GET** `/api/v1/cms/gallery/highlights/{id}/`

Returns details of a specific highlight.

**Response:** `200 OK`
```json
{
  "status": "success",
  "message": "Data retrieved successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Amazing Goal Compilation",
    "video_url": "https://res.cloudinary.com/.../highlights/video.mp4",
    "thumbnail_url": "https://res.cloudinary.com/.../highlights/thumbnails/thumb.jpg",
    "tags": ["goal", "skills", "tournament"],
    "is_active": true,
    "sort_order": 0,
    "created_at": "2026-09-10T10:30:00Z",
    "updated_at": "2026-09-10T10:30:00Z"
  }
}
```

**Error Response:** `404 Not Found`
```json
{
  "status": "error",
  "message": "Highlight not found"
}
```

---

### 4. Update Gallery Highlight
**PATCH** `/api/v1/cms/gallery/highlights/{id}/`

Update highlight metadata or replace video. **Admin only**.

**Request:** `multipart/form-data`
```
title: Updated Title (optional)
video: [new video file] (optional)
thumbnail: [new image file] (optional)
tags: ["goal", "highlight"] (optional)
is_active: false (optional)
sort_order: 5 (optional)
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "message": "Gallery highlight updated successfully.",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Updated Title",
    "video_url": "https://res.cloudinary.com/.../highlights/video.mp4",
    "thumbnail_url": null,
    "tags": ["goal", "highlight"],
    "is_active": false,
    "sort_order": 5,
    "created_at": "2026-09-10T10:30:00Z",
    "updated_at": "2026-09-10T15:45:00Z"
  }
}
```

---

### 5. Delete Gallery Highlight
**DELETE** `/api/v1/cms/gallery/highlights/{id}/`

Delete a highlight. **Admin only**.

**Response:** `200 OK`
```json
{
  "status": "success",
  "message": "Gallery highlight deleted successfully.",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Amazing Goal Compilation"
  }
}
```

---

## Cloudinary Storage

### Video Path
Videos are stored at: `highlights/{filename}`

**Example:**
- Original: `goal_compilation.mp4`
- Cloudinary: `https://res.cloudinary.com/{cloud_name}/video/upload/highlights/goal_compilation.mp4`

### Thumbnail Path
Thumbnails are stored at: `highlights/thumbnails/{filename}`

**Example:**
- Original: `thumbnail.jpg`
- Cloudinary: `https://res.cloudinary.com/{cloud_name}/image/upload/highlights/thumbnails/thumbnail.jpg`

### Max File Sizes
- Videos: 100 MB (configured in `futsal/settings.py`)
- Thumbnails: Standard image size limits

---

## Usage Examples

### Example 1: Upload Highlight with Tags (multipart/form-data)
```bash
curl -X POST "http://localhost:8000/api/v1/cms/gallery/highlights/" \
  -H "Authorization: Bearer {admin_token}" \
  -F "title=Best Saves 2026" \
  -F "video=@saves.mp4" \
  -F "thumbnail=@saves_thumb.jpg" \
  -F "tags=save, goalkeeper, 2026" \
  -F "is_active=true" \
  -F "sort_order=0"
```

### Example 2: Filter Active Highlights
```bash
curl "http://localhost:8000/api/v1/cms/gallery/highlights/?is_active=true"
```

### Example 3: Search by Tag
```bash
curl "http://localhost:8000/api/v1/cms/gallery/highlights/?search=goal"
```

### Example 4: Update Only Tags
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/gallery/highlights/{id}/" \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "tags": "goal, highlight, featured"
  }'
```

### Example 5: Deactivate Highlight
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/gallery/highlights/{id}/" \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

---

## Frontend Integration

### Display Highlights
```javascript
// Fetch all active highlights
const response = await fetch('/api/v1/cms/gallery/highlights/');
const { data } = await response.json();

data.results.forEach(highlight => {
  console.log(`Title: ${highlight.title}`);
  console.log(`Video: ${highlight.video_url}`);
  console.log(`Tags: ${highlight.tags.join(', ')}`);
});
```

### Filter by Tag
```javascript
// Search for specific tag
const response = await fetch('/api/v1/cms/gallery/highlights/?search=goal');
const { data } = await response.json();
```

### Upload New Highlight (Admin)
```javascript
const formData = new FormData();
formData.append('title', 'New Highlight');
formData.append('video', videoFile);
formData.append('thumbnail', thumbnailFile);
formData.append('tags', 'goal, tournament');
formData.append('is_active', 'true');

const response = await fetch('/api/v1/cms/gallery/highlights/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  },
  body: formData
});
```

---

## Admin Panel

Gallery highlights are manageable via Django Admin at `/admin/cms/galleryhighlight/`.

**Features:**
- List view with title, active status, sort order, creation date
- Search by title and tags
- Filter by active status and creation date
- Inline edit sort_order and is_active
- Video and thumbnail upload fields
- JSON editor for tags array

---

## Permissions

| Action | Public | Authenticated User | Admin |
|--------|--------|-------------------|-------|
| List (active only) | ✅ | ✅ | ✅ |
| List (all) | ❌ | ❌ | ✅ |
| View Detail | ✅ | ✅ | ✅ |
| Create | ❌ | ❌ | ✅ |
| Update | ❌ | ❌ | ✅ |
| Delete | ❌ | ❌ | ✅ |

---

## Technical Notes

1. **Video Format Support**: Cloudinary supports MP4, WebM, OGG, MOV, and other common video formats
2. **Tags Implementation**: Stored as TextField (plain text string)
3. **Thumbnail Optional**: Videos can be uploaded without thumbnails; Cloudinary can auto-generate if needed
4. **No Category**: Unlike gallery images, highlights use tags instead of categories for flexible filtering
5. **Ordering**: Default order is `sort_order` ascending, then `created_at` descending (newest first)
6. **Public Access**: Only active highlights are visible to non-admin users

---

## Database Schema

```sql
CREATE TABLE cms_gallery_highlight (
    id UUID PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    video VARCHAR(100) NOT NULL,
    thumbnail VARCHAR(100),
    tags JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_highlight_active_sort ON cms_gallery_highlight(is_active, sort_order);
```

---

## Related APIs

- **Gallery Categories**: `/api/v1/cms/gallery/category/`
- **Gallery Images**: `/api/v1/cms/gallery/images/`
- **Testimonials**: `/api/v1/cms/testimonials/`
- **Carousel**: `/api/v1/cms/homepage/carousel/`

---

## Migration Info

**Migration File**: `cms/migrations/0008_galleryhighlight.py`
**Applied**: Yes
**Dependencies**: 0007_galleryimage

---

## Testing Checklist

- [ ] Upload video highlight with tags
- [ ] Upload highlight without thumbnail
- [ ] List all highlights (public - active only)
- [ ] List all highlights (admin - including inactive)
- [ ] Search by title
- [ ] Search by tag text
- [ ] Filter by is_active
- [ ] Update title and tags
- [ ] Replace video file
- [ ] Update sort_order
- [ ] Deactivate highlight
- [ ] Delete highlight
- [ ] Verify Cloudinary paths correct
- [ ] Test tags as plain text
- [ ] Test negative sort_order rejection

---

**Last Updated**: September 10, 2026
**API Version**: v1
**Status**: ✅ Complete and Deployed
