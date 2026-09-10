# CMS Gallery Media API Documentation

## Overview

New API endpoints for managing CMS Gallery photos and videos with full CRUD operations (Create, Read, Update, Delete) including file uploads to Cloudinary.

## Implementation Status ✅

- ✅ Gallery Photo ViewSet with multipart upload
- ✅ Gallery Video ViewSet with multipart upload
- ✅ Upload serializers with validation
- ✅ Detail serializers for responses
- ✅ URL routing configured
- ✅ Swagger documentation generated
- ✅ Admin-only permissions
- ✅ Cache invalidation on changes
- ✅ Cloudinary file deletion on delete

## API Endpoints

### Gallery Photos

#### 1. List all gallery photos
```http
GET /api/v1/cms/gallery/photos/
```

**Query Parameters:**
- `category` - Filter by category (VENUE, MATCHES, COMMUNITY)
- `is_active` - Filter by active status (true/false)
- `ordering` - Sort by field (sort_order, created_at, -created_at)

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "key": "photo_abc123",
      "image_url": "https://res.cloudinary.com/.../photo.jpg",
      "alt_text": "Indoor court view",
      "title": "Main Arena",
      "category": "VENUE",
      "aspect_ratio": "16/9",
      "sort_order": 1,
      "is_active": true,
      "created_at": "2026-09-10T20:00:00Z",
      "updated_at": "2026-09-10T20:00:00Z"
    }
  ]
}
```

#### 2. Upload a new gallery photo
```http
POST /api/v1/cms/gallery/photos/
Content-Type: multipart/form-data
Authorization: Bearer {admin_token}
```

**Request Body (form-data):**
```
image: [file] (required on create)
title: "Main Arena" (required)
alt_text: "Indoor court view" (required)
category: "VENUE" (required: VENUE|MATCHES|COMMUNITY)
aspect_ratio: "16/9" (optional, default: 4/3, valid: 16/10, 16/9, 4/3, 1/1, 3/4)
sort_order: 1 (optional, default: 0)
is_active: true (optional, default: true)
key: "photo_abc123" (optional, auto-generated if not provided)
```

**Response:** (201 Created)
```json
{
  "status": "success",
  "message": "Gallery photo uploaded successfully.",
  "data": {
    "id": "uuid",
    "key": "photo_abc123",
    "image_url": "https://res.cloudinary.com/.../photo.jpg",
    "alt_text": "Indoor court view",
    "title": "Main Arena",
    "category": "VENUE",
    "aspect_ratio": "16/9",
    "sort_order": 1,
    "is_active": true,
    "created_at": "2026-09-10T20:00:00Z",
    "updated_at": "2026-09-10T20:00:00Z"
  }
}
```

#### 3. Get photo details
```http
GET /api/v1/cms/gallery/photos/{id}/
```

**Response:** Same as list item above

#### 4. Update photo metadata or replace image
```http
PATCH /api/v1/cms/gallery/photos/{id}/
Content-Type: multipart/form-data
Authorization: Bearer {admin_token}
```

**Request Body (form-data):**
```
# Only include fields you want to change
image: [file] (optional - replaces the image)
title: "Updated Title" (optional)
alt_text: "Updated alt text" (optional)
category: "MATCHES" (optional)
aspect_ratio: "4/3" (optional)
sort_order: 10 (optional)
is_active: false (optional)
```

**Response:** (200 OK)
```json
{
  "status": "success",
  "message": "Gallery photo updated successfully.",
  "data": { /* updated photo data */ }
}
```

#### 5. Delete photo
```http
DELETE /api/v1/cms/gallery/photos/{id}/
Authorization: Bearer {admin_token}
```

**Response:** (200 OK)
```json
{
  "status": "success",
  "message": "Gallery photo deleted successfully.",
  "data": {
    "id": "uuid",
    "title": "Main Arena"
  }
}
```

**Note:** This also deletes the image file from Cloudinary.

---

### Gallery Videos

#### 1. List all gallery videos
```http
GET /api/v1/cms/gallery/videos/
```

**Query Parameters:**
- `category` - Filter by category (VENUE, MATCHES, COMMUNITY)
- `is_active` - Filter by active status (true/false)
- `ordering` - Sort by field (sort_order, created_at, -created_at)

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "key": "video_xyz456",
      "video_url": "https://res.cloudinary.com/.../video.mp4",
      "poster_url": "https://res.cloudinary.com/.../poster.jpg",
      "title": "Match Highlights",
      "category": "MATCHES",
      "duration_seconds": 120,
      "sort_order": 1,
      "is_active": true,
      "created_at": "2026-09-10T20:00:00Z",
      "updated_at": "2026-09-10T20:00:00Z"
    }
  ]
}
```

#### 2. Upload a new gallery video
```http
POST /api/v1/cms/gallery/videos/
Content-Type: multipart/form-data
Authorization: Bearer {admin_token}
```

**Request Body (form-data):**
```
video: [file] (required on create)
poster: [file] (required on create - thumbnail/poster image)
title: "Match Highlights" (required)
category: "MATCHES" (required: VENUE|MATCHES|COMMUNITY)
duration_seconds: 120 (required)
sort_order: 1 (optional, default: 0)
is_active: true (optional, default: true)
key: "video_xyz456" (optional, auto-generated if not provided)
```

**Response:** (201 Created)
```json
{
  "status": "success",
  "message": "Gallery video uploaded successfully.",
  "data": {
    "id": "uuid",
    "key": "video_xyz456",
    "video_url": "https://res.cloudinary.com/.../video.mp4",
    "poster_url": "https://res.cloudinary.com/.../poster.jpg",
    "title": "Match Highlights",
    "category": "MATCHES",
    "duration_seconds": 120,
    "sort_order": 1,
    "is_active": true,
    "created_at": "2026-09-10T20:00:00Z",
    "updated_at": "2026-09-10T20:00:00Z"
  }
}
```

#### 3. Get video details
```http
GET /api/v1/cms/gallery/videos/{id}/
```

**Response:** Same as list item above

#### 4. Update video metadata or replace files
```http
PATCH /api/v1/cms/gallery/videos/{id}/
Content-Type: multipart/form-data
Authorization: Bearer {admin_token}
```

**Request Body (form-data):**
```
# Only include fields you want to change
video: [file] (optional - replaces the video)
poster: [file] (optional - replaces the poster)
title: "Updated Title" (optional)
category: "COMMUNITY" (optional)
duration_seconds: 150 (optional)
sort_order: 10 (optional)
is_active: false (optional)
```

**Response:** (200 OK)
```json
{
  "status": "success",
  "message": "Gallery video updated successfully.",
  "data": { /* updated video data */ }
}
```

#### 5. Delete video
```http
DELETE /api/v1/cms/gallery/videos/{id}/
Authorization: Bearer {admin_token}
```

**Response:** (200 OK)
```json
{
  "status": "success",
  "message": "Gallery video deleted successfully.",
  "data": {
    "id": "uuid",
    "title": "Match Highlights"
  }
}
```

**Note:** This also deletes both the video file and poster image from Cloudinary.

---

## Categories

Valid category values for both photos and videos:
- `VENUE` - Venue/facility photos
- `MATCHES` - Match action shots and highlights
- `COMMUNITY` - Community events, teams, players

The gallery page frontend can filter by these categories.

## Aspect Ratios (Photos Only)

Valid aspect ratio values:
- `16/10` - Wide landscape
- `16/9` - Standard widescreen
- `4/3` - Traditional landscape
- `1/1` - Square
- `3/4` - Portrait

The frontend uses these for responsive masonry grid layouts.

## Validation Rules

### Photos
- Image file required on creation
- Valid image formats: JPG, PNG, WebP (configured in validators)
- Max file size: Configured in Cloudinary settings
- Alt text required for accessibility

### Videos
- Video file required on creation
- Poster image required on creation
- Duration must be positive integer (seconds)
- Valid video formats: MP4, WebM, MOV (configured in validators)
- Max file size: Configured in Cloudinary settings

## Security & Permissions

- **GET endpoints**: Public (same as page endpoints)
- **POST/PATCH/DELETE endpoints**: Admin-only (`IsAuthenticated` + `IsAdmin`)
- **File storage**: Cloudinary with secure URLs
- **File deletion**: Automatic cleanup on DELETE operations

## Cache Management

All create/update/delete operations automatically invalidate the gallery page cache:
```python
cache.delete("cms:gallery:data")
```

This ensures the GET `/api/v1/cms/gallery/` endpoint always returns fresh data after media changes.

## Frontend Integration Examples

### Upload Photo with JavaScript

```javascript
async function uploadGalleryPhoto(file, metadata) {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('title', metadata.title);
  formData.append('alt_text', metadata.altText);
  formData.append('category', metadata.category);
  formData.append('aspect_ratio', metadata.aspectRatio || '4/3');
  formData.append('sort_order', metadata.sortOrder || 0);
  
  const response = await fetch('/api/v1/cms/gallery/photos/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${adminToken}`
    },
    body: formData
  });
  
  const result = await response.json();
  
  if (result.status === 'success') {
    console.log('Photo uploaded:', result.data);
    return result.data;
  } else {
    throw new Error(result.message || 'Upload failed');
  }
}

// Usage
const fileInput = document.getElementById('photo-upload');
const file = fileInput.files[0];

uploadGalleryPhoto(file, {
  title: 'Indoor Arena',
  altText: 'Main indoor futsal court',
  category: 'VENUE',
  aspectRatio: '16/9',
  sortOrder: 1
});
```

### Upload Video with React

```javascript
import { useState } from 'react';

function VideoUploadForm() {
  const [videoFile, setVideoFile] = useState(null);
  const [posterFile, setPosterFile] = useState(null);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('MATCHES');
  const [duration, setDuration] = useState(0);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('poster', posterFile);
    formData.append('title', title);
    formData.append('category', category);
    formData.append('duration_seconds', duration);
    
    const response = await fetch('/api/v1/cms/gallery/videos/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${adminToken}`
      },
      body: formData
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      alert('Video uploaded successfully!');
      // Reset form or redirect
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input type="file" accept="video/*" onChange={(e) => setVideoFile(e.target.files[0])} required />
      <input type="file" accept="image/*" onChange={(e) => setPosterFile(e.target.files[0])} required />
      <input type="text" placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} required />
      <select value={category} onChange={(e) => setCategory(e.target.value)}>
        <option value="VENUE">Venue</option>
        <option value="MATCHES">Matches</option>
        <option value="COMMUNITY">Community</option>
      </select>
      <input type="number" placeholder="Duration (seconds)" value={duration} onChange={(e) => setDuration(e.target.value)} required />
      <button type="submit">Upload Video</button>
    </form>
  );
}
```

### Delete Media

```javascript
async function deleteGalleryPhoto(photoId) {
  const confirmed = confirm('Are you sure you want to delete this photo?');
  if (!confirmed) return;
  
  const response = await fetch(`/api/v1/cms/gallery/photos/${photoId}/`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${adminToken}`
    }
  });
  
  const result = await response.json();
  
  if (result.status === 'success') {
    console.log('Photo deleted:', result.data);
    // Refresh list
  }
}

async function deleteGalleryVideo(videoId) {
  const confirmed = confirm('Are you sure you want to delete this video?');
  if (!confirmed) return;
  
  const response = await fetch(`/api/v1/cms/gallery/videos/${videoId}/`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${adminToken}`
    }
  });
  
  const result = await response.json();
  
  if (result.status === 'success') {
    console.log('Video deleted:', result.data);
    // Refresh list
  }
}
```

### Filter by Category

```javascript
async function getGalleryPhotos(category = null, activeOnly = true) {
  let url = '/api/v1/cms/gallery/photos/';
  const params = new URLSearchParams();
  
  if (category) params.append('category', category);
  if (activeOnly) params.append('is_active', 'true');
  params.append('ordering', 'sort_order');
  
  const queryString = params.toString();
  if (queryString) url += `?${queryString}`;
  
  const response = await fetch(url);
  const result = await response.json();
  
  return result.data;
}

// Get all venue photos
const venuePhotos = await getGalleryPhotos('VENUE');

// Get all match videos
const matchVideos = await getGalleryVideos('MATCHES');
```

## Comparison: FutsalMedia vs CMS Gallery

| Feature | FutsalMedia API | CMS Gallery API |
|---------|-----------------|-----------------|
| **Endpoint** | `/api/v1/admin/media/` | `/api/v1/cms/gallery/photos/`, `/api/v1/cms/gallery/videos/` |
| **Purpose** | General venue photos | Categorized gallery page |
| **Categories** | ❌ None | ✅ VENUE/MATCHES/COMMUNITY |
| **Alt Text** | Caption only | Full alt text for accessibility |
| **Aspect Ratio** | ❌ No | ✅ Yes (5 options) |
| **Video Poster** | ❌ No | ✅ Yes (required) |
| **Duration** | ❌ No | ✅ Yes (required for videos) |
| **Cover Flag** | ✅ Yes (is_cover) | ❌ No |
| **Used In** | Futsal info, homepage | Gallery page only |
| **Model** | FutsalMedia | GalleryPhoto, GalleryVideo |

**Recommendation:** Keep both systems separate as they serve different purposes.

---

## Testing

You can test the endpoints using:

1. **Swagger UI**: http://localhost:8000/api/v1/docs/
   - Navigate to "cms" tag
   - Find "Gallery Photos" and "Gallery Videos" sections
   - Use "Try it out" to test uploads

2. **Postman/Insomnia**: Import the schema.yml and test endpoints

3. **cURL Examples**:

```bash
# Upload photo
curl -X POST http://localhost:8000/api/v1/cms/gallery/photos/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "image=@photo.jpg" \
  -F "title=Indoor Arena" \
  -F "alt_text=Main indoor court" \
  -F "category=VENUE" \
  -F "aspect_ratio=16/9"

# List photos
curl http://localhost:8000/api/v1/cms/gallery/photos/?category=VENUE

# Delete photo
curl -X DELETE http://localhost:8000/api/v1/cms/gallery/photos/{id}/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Summary

✅ **Complete CRUD API** for CMS gallery photos and videos  
✅ **Multipart file uploads** with validation  
✅ **Cloudinary integration** with automatic file deletion  
✅ **Category-based organization** (VENUE/MATCHES/COMMUNITY)  
✅ **Admin-only permissions** for security  
✅ **Cache invalidation** for fresh data  
✅ **Swagger documentation** for easy testing  
✅ **Separate from FutsalMedia** (no breaking changes)

The CMS Gallery now has full media management capabilities! 🚀
