# Gallery CMS Integration Guide

**Complete integration reference for Gallery CMS with real data examples**

This document contains everything you need to integrate the Gallery CMS, including:
- All endpoints with full request/response examples
- Real pre-filled data for testing
- Step-by-step integration workflows
- Frontend code examples

---

## Table of Contents

1. [Overview](#overview)
2. [Public Gallery Page API](#public-gallery-page-api)
3. [Gallery Page Content Management](#gallery-page-content-management)
4. [Gallery Photos Management](#gallery-photos-management)
5. [Gallery Videos Management](#gallery-videos-management)
6. [Complete Integration Workflows](#complete-integration-workflows)
7. [Frontend Examples](#frontend-examples)

---

## Overview

### System Architecture

```
Gallery CMS consists of 3 independent systems:

1. Gallery Page Content (text: headers, descriptions, categories, CTA)
   └── Endpoints: GET + PATCH /api/v1/cms/gallery/

2. Gallery Photos (image files + metadata)
   └── Endpoints: Full CRUD /api/v1/cms/gallery/photos/

3. Gallery Videos (video files + posters + metadata)
   └── Endpoints: Full CRUD /api/v1/cms/gallery/videos/
```

### Key Points

✅ **Gallery GET response** includes everything (text + photos + videos)  
✅ **Gallery PATCH** only updates text content (headers, descriptions)  
✅ **Photos/Videos APIs** handle file uploads and individual media management  
✅ All changes auto-refresh the Gallery GET response (cache invalidation)

---

## Public Gallery Page API

### 🔵 GET - Retrieve Complete Gallery Page

**Endpoint:**
```
GET /api/v1/cms/gallery/
```

**Authentication:** None (Public)

**Description:** Returns complete gallery page content including all text, photos, and videos.

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/cms/gallery/"
```

**Response Example (200 OK):**
```json
{
  "status": "success",
  "message": "Gallery page content retrieved successfully.",
  "data": {
    "meta_title": "Gallery - Nexus Futsal",
    "meta_description": "Browse our collection of photos and videos showcasing our world-class futsal facility, exciting matches, and vibrant community.",
    "updated_at": "2026-09-10T19:30:00Z",
    
    "header": {
      "eyebrow": "Photo & Video Gallery",
      "title": "Moments that matter",
      "description": "From intense matches to community events, explore the energy and passion that make Nexus Futsal more than just a venue."
    },
    
    "categories": [
      {
        "key": "ALL",
        "label": "All Media"
      },
      {
        "key": "VENUE",
        "label": "Venue & Facilities"
      },
      {
        "key": "MATCHES",
        "label": "Match Action"
      },
      {
        "key": "COMMUNITY",
        "label": "Community & Events"
      }
    ],
    
    "photos": [
      {
        "key": "indoor_arena_main",
        "url": "https://res.cloudinary.com/demo/image/upload/v1/futsal/indoor-arena.jpg",
        "alt_text": "Main indoor futsal court with professional lighting and pristine turf",
        "title": "Main Indoor Arena",
        "category": "VENUE",
        "aspect_ratio": "16/9"
      },
      {
        "key": "match_action_goal",
        "url": "https://res.cloudinary.com/demo/image/upload/v1/futsal/goal-celebration.jpg",
        "alt_text": "Players celebrating a goal during an intense match",
        "title": "Victory Moment",
        "category": "MATCHES",
        "aspect_ratio": "4/3"
      },
      {
        "key": "community_tournament",
        "url": "https://res.cloudinary.com/demo/image/upload/v1/futsal/tournament-teams.jpg",
        "alt_text": "Teams posing together during community tournament",
        "title": "Monthly Tournament",
        "category": "COMMUNITY",
        "aspect_ratio": "16/10"
      },
      {
        "key": "locker_rooms",
        "url": "https://res.cloudinary.com/demo/image/upload/v1/futsal/locker-room.jpg",
        "alt_text": "Clean modern locker room with benches and lockers",
        "title": "Locker Room Facilities",
        "category": "VENUE",
        "aspect_ratio": "4/3"
      },
      {
        "key": "night_match",
        "url": "https://res.cloudinary.com/demo/image/upload/v1/futsal/night-game.jpg",
        "alt_text": "Exciting night match with stadium lights",
        "title": "Night Game Atmosphere",
        "category": "MATCHES",
        "aspect_ratio": "16/9"
      }
    ],
    
    "videos_section": {
      "heading": "Highlights & Clips",
      "description": "Short clips from around the arena — press play to experience the action.",
      "videos": [
        {
          "key": "facility_tour",
          "url": "https://res.cloudinary.com/demo/video/upload/v1/futsal/facility-tour.mp4",
          "poster": "https://res.cloudinary.com/demo/image/upload/v1/futsal/facility-tour-poster.jpg",
          "title": "Complete Facility Tour",
          "category": "VENUE",
          "duration_seconds": 90
        },
        {
          "key": "match_highlights_jan",
          "url": "https://res.cloudinary.com/demo/video/upload/v1/futsal/match-highlights.mp4",
          "poster": "https://res.cloudinary.com/demo/image/upload/v1/futsal/match-poster.jpg",
          "title": "January Match Highlights",
          "category": "MATCHES",
          "duration_seconds": 120
        },
        {
          "key": "community_event",
          "url": "https://res.cloudinary.com/demo/video/upload/v1/futsal/community-day.mp4",
          "poster": "https://res.cloudinary.com/demo/image/upload/v1/futsal/community-poster.jpg",
          "title": "Community Day Recap",
          "category": "COMMUNITY",
          "duration_seconds": 75
        }
      ]
    },
    
    "cta": {
      "heading": "Ready to play?",
      "description": "Book your slot today and become part of our story.",
      "button": {
        "label": "View Available Slots",
        "href": "/bookings",
        "style": "primary"
      }
    }
  }
}
```

**Use Case:** Public gallery page rendering

---

## Gallery Page Content Management

### 🟡 PATCH - Update Gallery Page Text Content

**Endpoint:**
```
PATCH /api/v1/cms/gallery/
```

**Authentication:** Required (Admin only)

**Content-Type:** `application/json`

**Description:** Updates gallery page text content (headers, descriptions, categories, CTA). Does NOT handle photo/video uploads.

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Body Example (Partial Update):**
```json
{
  "meta_title": "Photo Gallery - Nexus Futsal Arena",
  "header_title": "Capture the Energy",
  "header_description": "Every match, every moment, every celebration - witness the passion that drives our futsal community.",
  "videos_section_heading": "Video Highlights",
  "cta_heading": "Join the Action"
}
```

**Full Request Body Example (All Fields):**
```json
{
  "meta_title": "Gallery - Nexus Futsal",
  "meta_description": "Explore photos and videos from Nexus Futsal - matches, facilities, and community events.",
  
  "header_eyebrow": "Photo & Video Gallery",
  "header_title": "Moments that matter",
  "header_description": "From intense matches to community events, explore the energy and passion that make Nexus Futsal more than just a venue.",
  
  "categories": [
    {
      "key": "ALL",
      "label": "All Media",
      "is_active": true
    },
    {
      "key": "VENUE",
      "label": "Venue & Facilities",
      "is_active": true
    },
    {
      "key": "MATCHES",
      "label": "Match Action",
      "is_active": true
    },
    {
      "key": "COMMUNITY",
      "label": "Community & Events",
      "is_active": true
    }
  ],
  
  "videos_section_heading": "Highlights & Clips",
  "videos_section_description": "Short clips from around the arena — press play to experience the action.",
  
  "cta_heading": "Ready to play?",
  "cta_description": "Book your slot today and become part of our story.",
  "cta_button_label": "View Available Slots",
  "cta_button_href": "/bookings",
  "cta_button_style": "primary"
}
```

**Response Example (200 OK):**
```json
{
  "status": "success",
  "message": "Gallery page content updated successfully.",
  "data": {
    "meta_title": "Photo Gallery - Nexus Futsal Arena",
    "meta_description": "Explore photos and videos from Nexus Futsal - matches, facilities, and community events.",
    "updated_at": "2026-09-10T20:15:00Z",
    
    "header": {
      "eyebrow": "Photo & Video Gallery",
      "title": "Capture the Energy",
      "description": "Every match, every moment, every celebration - witness the passion that drives our futsal community."
    },
    
    "categories": [
      { "key": "ALL", "label": "All Media" },
      { "key": "VENUE", "label": "Venue & Facilities" },
      { "key": "MATCHES", "label": "Match Action" },
      { "key": "COMMUNITY", "label": "Community & Events" }
    ],
    
    "photos": [ /* existing photos unchanged */ ],
    
    "videos_section": {
      "heading": "Video Highlights",
      "description": "Short clips from around the arena — press play to experience the action.",
      "videos": [ /* existing videos unchanged */ ]
    },
    
    "cta": {
      "heading": "Join the Action",
      "description": "Book your slot today and become part of our story.",
      "button": {
        "label": "View Available Slots",
        "href": "/bookings",
        "style": "primary"
      }
    }
  }
}
```

**cURL Example:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/gallery/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "meta_title": "Photo Gallery - Nexus Futsal Arena",
    "header_title": "Capture the Energy",
    "cta_heading": "Join the Action"
  }'
```

**Use Case:** Admin updating page headers, descriptions, and CTA text

---

## Gallery Photos Management

### 🟢 GET - List All Gallery Photos

**Endpoint:**
```
GET /api/v1/cms/gallery/photos/
```

**Authentication:** None (Public)

**Query Parameters:**
- `category` (optional): Filter by category (VENUE, MATCHES, COMMUNITY)
- `is_active` (optional): Filter by active status (true, false)
- `ordering` (optional): Sort results (sort_order, -sort_order, created_at, -created_at)

**Request Example:**
```bash
# Get all photos
curl -X GET "http://localhost:8000/api/v1/cms/gallery/photos/"

# Get only venue photos
curl -X GET "http://localhost:8000/api/v1/cms/gallery/photos/?category=VENUE"

# Get active photos sorted by sort_order
curl -X GET "http://localhost:8000/api/v1/cms/gallery/photos/?is_active=true&ordering=sort_order"
```

**Response Example (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "key": "indoor_arena_main",
      "image_url": "https://res.cloudinary.com/demo/image/upload/v1/futsal/indoor-arena.jpg",
      "alt_text": "Main indoor futsal court with professional lighting and pristine turf",
      "title": "Main Indoor Arena",
      "category": "VENUE",
      "aspect_ratio": "16/9",
      "sort_order": 1,
      "is_active": true,
      "created_at": "2026-09-05T10:00:00Z",
      "updated_at": "2026-09-05T10:00:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "key": "match_action_goal",
      "image_url": "https://res.cloudinary.com/demo/image/upload/v1/futsal/goal-celebration.jpg",
      "alt_text": "Players celebrating a goal during an intense match",
      "title": "Victory Moment",
      "category": "MATCHES",
      "aspect_ratio": "4/3",
      "sort_order": 2,
      "is_active": true,
      "created_at": "2026-09-06T14:30:00Z",
      "updated_at": "2026-09-06T14:30:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "key": "community_tournament",
      "image_url": "https://res.cloudinary.com/demo/image/upload/v1/futsal/tournament-teams.jpg",
      "alt_text": "Teams posing together during community tournament",
      "title": "Monthly Tournament",
      "category": "COMMUNITY",
      "aspect_ratio": "16/10",
      "sort_order": 3,
      "is_active": true,
      "created_at": "2026-09-07T16:00:00Z",
      "updated_at": "2026-09-07T16:00:00Z"
    }
  ]
}
```

**Use Case:** Admin viewing all photos in gallery management UI

---

### 🟢 POST - Upload New Gallery Photo

**Endpoint:**
```
POST /api/v1/cms/gallery/photos/
```

**Authentication:** Required (Admin only)

**Content-Type:** `multipart/form-data`

**Description:** Uploads a new photo with metadata to the gallery.

**Request Headers:**
```
Content-Type: multipart/form-data
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Body (form-data):**
```
image: [Binary file: indoor-court.jpg]
title: "Indoor Court View"
alt_text: "Wide angle view of the indoor futsal court with professional lighting"
category: "VENUE"
aspect_ratio: "16/9"
sort_order: 10
is_active: true
```

**Full Field Reference:**
```
image (required): Image file (JPEG, PNG, WebP)
title (required): Photo title (max 200 chars)
alt_text (required): Alt text for accessibility (max 200 chars)
category (required): VENUE | MATCHES | COMMUNITY
aspect_ratio (optional): 16/10 | 16/9 | 4/3 | 1/1 | 3/4 (default: 4/3)
sort_order (optional): Integer (default: 0)
is_active (optional): Boolean (default: true)
key (optional): Unique identifier (auto-generated if not provided)
```

**Response Example (201 Created):**
```json
{
  "status": "success",
  "message": "Gallery photo uploaded successfully.",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440010",
    "key": "photo_a3f2b9c1",
    "image_url": "https://res.cloudinary.com/demo/image/upload/v1726086234/cms/gallery/photos/indoor-court.jpg",
    "alt_text": "Wide angle view of the indoor futsal court with professional lighting",
    "title": "Indoor Court View",
    "category": "VENUE",
    "aspect_ratio": "16/9",
    "sort_order": 10,
    "is_active": true,
    "created_at": "2026-09-10T20:30:34Z",
    "updated_at": "2026-09-10T20:30:34Z"
  }
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/cms/gallery/photos/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "image=@/path/to/indoor-court.jpg" \
  -F "title=Indoor Court View" \
  -F "alt_text=Wide angle view of the indoor futsal court with professional lighting" \
  -F "category=VENUE" \
  -F "aspect_ratio=16/9" \
  -F "sort_order=10" \
  -F "is_active=true"
```

**JavaScript Example:**
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('title', 'Indoor Court View');
formData.append('alt_text', 'Wide angle view of the indoor futsal court with professional lighting');
formData.append('category', 'VENUE');
formData.append('aspect_ratio', '16/9');
formData.append('sort_order', '10');
formData.append('is_active', 'true');

const response = await fetch('/api/v1/cms/gallery/photos/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  },
  body: formData
});

const result = await response.json();
console.log(result.data); // New photo data
```

**Use Case:** Admin uploading a new photo to the gallery

---

### 🟢 GET - Get Single Photo Details

**Endpoint:**
```
GET /api/v1/cms/gallery/photos/{id}/
```

**Authentication:** None (Public)

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/cms/gallery/photos/550e8400-e29b-41d4-a716-446655440001/"
```

**Response Example (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "key": "indoor_arena_main",
    "image_url": "https://res.cloudinary.com/demo/image/upload/v1/futsal/indoor-arena.jpg",
    "alt_text": "Main indoor futsal court with professional lighting and pristine turf",
    "title": "Main Indoor Arena",
    "category": "VENUE",
    "aspect_ratio": "16/9",
    "sort_order": 1,
    "is_active": true,
    "created_at": "2026-09-05T10:00:00Z",
    "updated_at": "2026-09-05T10:00:00Z"
  }
}
```

**Use Case:** Viewing specific photo details in admin panel

---

### 🟡 PATCH - Update Gallery Photo

**Endpoint:**
```
PATCH /api/v1/cms/gallery/photos/{id}/
```

**Authentication:** Required (Admin only)

**Content-Type:** `multipart/form-data` or `application/json`

**Description:** Updates photo metadata or replaces the image file. Only include fields you want to change.

**Request Headers:**
```
Content-Type: multipart/form-data
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Body Example 1 (Update metadata only - JSON):**
```json
{
  "title": "Updated Arena View",
  "alt_text": "Updated description of the main indoor court",
  "category": "VENUE",
  "sort_order": 5
}
```

**Request Body Example 2 (Replace image - form-data):**
```
image: [Binary file: new-arena-photo.jpg]
title: "New Arena Photo"
```

**Request Body Example 3 (Update multiple fields - form-data):**
```
title: "Premium Indoor Court"
alt_text: "Newly renovated indoor court with LED lighting"
category: "VENUE"
aspect_ratio: "16/10"
sort_order: 1
is_active: true
```

**Response Example (200 OK):**
```json
{
  "status": "success",
  "message": "Gallery photo updated successfully.",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "key": "indoor_arena_main",
    "image_url": "https://res.cloudinary.com/demo/image/upload/v1726086500/cms/gallery/photos/new-arena-photo.jpg",
    "alt_text": "Newly renovated indoor court with LED lighting",
    "title": "Premium Indoor Court",
    "category": "VENUE",
    "aspect_ratio": "16/10",
    "sort_order": 1,
    "is_active": true,
    "created_at": "2026-09-05T10:00:00Z",
    "updated_at": "2026-09-10T20:35:00Z"
  }
}
```

**cURL Example (Update metadata):**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/gallery/photos/550e8400-e29b-41d4-a716-446655440001/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "title": "Premium Indoor Court",
    "sort_order": 1
  }'
```

**cURL Example (Replace image):**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/gallery/photos/550e8400-e29b-41d4-a716-446655440001/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "image=@/path/to/new-photo.jpg" \
  -F "title=Updated Photo"
```

**JavaScript Example:**
```javascript
// Update metadata only
const response = await fetch(`/api/v1/cms/gallery/photos/${photoId}/`, {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${adminToken}`
  },
  body: JSON.stringify({
    title: 'Updated Title',
    sort_order: 5
  })
});

// Replace image
const formData = new FormData();
formData.append('image', newFile);
formData.append('title', 'Updated Photo');

const response = await fetch(`/api/v1/cms/gallery/photos/${photoId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  },
  body: formData
});
```

**Use Case:** Admin editing photo metadata or replacing an image

---

### 🔴 DELETE - Delete Gallery Photo

**Endpoint:**
```
DELETE /api/v1/cms/gallery/photos/{id}/
```

**Authentication:** Required (Admin only)

**Description:** Deletes the photo from database and removes the image file from Cloudinary.

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/cms/gallery/photos/550e8400-e29b-41d4-a716-446655440001/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Response Example (200 OK):**
```json
{
  "status": "success",
  "message": "Gallery photo deleted successfully.",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Main Indoor Arena"
  }
}
```

**JavaScript Example:**
```javascript
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
  // Remove from UI
  removePhotoFromDOM(photoId);
}
```

**Use Case:** Admin deleting unwanted photos

---

## Gallery Videos Management

### 🟢 GET - List All Gallery Videos

**Endpoint:**
```
GET /api/v1/cms/gallery/videos/
```

**Authentication:** None (Public)

**Query Parameters:**
- `category` (optional): Filter by category (VENUE, MATCHES, COMMUNITY)
- `is_active` (optional): Filter by active status (true, false)
- `ordering` (optional): Sort results (sort_order, -sort_order, created_at, -created_at)

**Request Example:**
```bash
# Get all videos
curl -X GET "http://localhost:8000/api/v1/cms/gallery/videos/"

# Get only match videos
curl -X GET "http://localhost:8000/api/v1/cms/gallery/videos/?category=MATCHES"

# Get active videos sorted by creation date
curl -X GET "http://localhost:8000/api/v1/cms/gallery/videos/?is_active=true&ordering=-created_at"
```

**Response Example (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440101",
      "key": "facility_tour",
      "video_url": "https://res.cloudinary.com/demo/video/upload/v1/futsal/facility-tour.mp4",
      "poster_url": "https://res.cloudinary.com/demo/image/upload/v1/futsal/facility-tour-poster.jpg",
      "title": "Complete Facility Tour",
      "category": "VENUE",
      "duration_seconds": 90,
      "sort_order": 1,
      "is_active": true,
      "created_at": "2026-09-05T11:00:00Z",
      "updated_at": "2026-09-05T11:00:00Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440102",
      "key": "match_highlights_jan",
      "video_url": "https://res.cloudinary.com/demo/video/upload/v1/futsal/match-highlights.mp4",
      "poster_url": "https://res.cloudinary.com/demo/image/upload/v1/futsal/match-poster.jpg",
      "title": "January Match Highlights",
      "category": "MATCHES",
      "duration_seconds": 120,
      "sort_order": 2,
      "is_active": true,
      "created_at": "2026-09-06T15:30:00Z",
      "updated_at": "2026-09-06T15:30:00Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440103",
      "key": "community_event",
      "video_url": "https://res.cloudinary.com/demo/video/upload/v1/futsal/community-day.mp4",
      "poster_url": "https://res.cloudinary.com/demo/image/upload/v1/futsal/community-poster.jpg",
      "title": "Community Day Recap",
      "category": "COMMUNITY",
      "duration_seconds": 75,
      "sort_order": 3,
      "is_active": true,
      "created_at": "2026-09-07T17:00:00Z",
      "updated_at": "2026-09-07T17:00:00Z"
    }
  ]
}
```

**Use Case:** Admin viewing all videos in gallery management UI

---

### 🟢 POST - Upload New Gallery Video

**Endpoint:**
```
POST /api/v1/cms/gallery/videos/
```

**Authentication:** Required (Admin only)

**Content-Type:** `multipart/form-data`

**Description:** Uploads a new video with poster image and metadata to the gallery.

**Request Headers:**
```
Content-Type: multipart/form-data
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Body (form-data):**
```
video: [Binary file: match-highlights.mp4]
poster: [Binary file: match-poster.jpg]
title: "February Match Highlights"
category: "MATCHES"
duration_seconds: 135
sort_order: 5
is_active: true
```

**Full Field Reference:**
```
video (required): Video file (MP4, WebM, MOV)
poster (required): Poster/thumbnail image (JPEG, PNG, WebP)
title (required): Video title (max 200 chars)
category (required): VENUE | MATCHES | COMMUNITY
duration_seconds (required): Video duration in seconds (integer)
sort_order (optional): Integer (default: 0)
is_active (optional): Boolean (default: true)
key (optional): Unique identifier (auto-generated if not provided)
```

**Response Example (201 Created):**
```json
{
  "status": "success",
  "message": "Gallery video uploaded successfully.",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440110",
    "key": "video_f8d3c2a7",
    "video_url": "https://res.cloudinary.com/demo/video/upload/v1726086700/cms/gallery/videos/match-highlights.mp4",
    "poster_url": "https://res.cloudinary.com/demo/image/upload/v1726086700/cms/gallery/posters/match-poster.jpg",
    "title": "February Match Highlights",
    "category": "MATCHES",
    "duration_seconds": 135,
    "sort_order": 5,
    "is_active": true,
    "created_at": "2026-09-10T20:45:00Z",
    "updated_at": "2026-09-10T20:45:00Z"
  }
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/cms/gallery/videos/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "video=@/path/to/match-highlights.mp4" \
  -F "poster=@/path/to/match-poster.jpg" \
  -F "title=February Match Highlights" \
  -F "category=MATCHES" \
  -F "duration_seconds=135" \
  -F "sort_order=5" \
  -F "is_active=true"
```

**JavaScript Example:**
```javascript
const formData = new FormData();
formData.append('video', videoFileInput.files[0]);
formData.append('poster', posterFileInput.files[0]);
formData.append('title', 'February Match Highlights');
formData.append('category', 'MATCHES');
formData.append('duration_seconds', '135');
formData.append('sort_order', '5');
formData.append('is_active', 'true');

const response = await fetch('/api/v1/cms/gallery/videos/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  },
  body: formData
});

const result = await response.json();
console.log(result.data); // New video data
```

**Use Case:** Admin uploading a new video to the gallery

---

### 🟢 GET - Get Single Video Details

**Endpoint:**
```
GET /api/v1/cms/gallery/videos/{id}/
```

**Authentication:** None (Public)

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/cms/gallery/videos/660e8400-e29b-41d4-a716-446655440101/"
```

**Response Example (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440101",
    "key": "facility_tour",
    "video_url": "https://res.cloudinary.com/demo/video/upload/v1/futsal/facility-tour.mp4",
    "poster_url": "https://res.cloudinary.com/demo/image/upload/v1/futsal/facility-tour-poster.jpg",
    "title": "Complete Facility Tour",
    "category": "VENUE",
    "duration_seconds": 90,
    "sort_order": 1,
    "is_active": true,
    "created_at": "2026-09-05T11:00:00Z",
    "updated_at": "2026-09-05T11:00:00Z"
  }
}
```

**Use Case:** Viewing specific video details in admin panel

---

### 🟡 PATCH - Update Gallery Video

**Endpoint:**
```
PATCH /api/v1/cms/gallery/videos/{id}/
```

**Authentication:** Required (Admin only)

**Content-Type:** `multipart/form-data` or `application/json`

**Description:** Updates video metadata, replaces video file, or updates poster image. Only include fields you want to change.

**Request Headers:**
```
Content-Type: multipart/form-data
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Body Example 1 (Update metadata only - JSON):**
```json
{
  "title": "Updated Match Highlights",
  "category": "MATCHES",
  "duration_seconds": 140,
  "sort_order": 1
}
```

**Request Body Example 2 (Replace video file - form-data):**
```
video: [Binary file: new-highlights.mp4]
title: "New Match Highlights"
duration_seconds: 150
```

**Request Body Example 3 (Update poster only - form-data):**
```
poster: [Binary file: new-poster.jpg]
```

**Request Body Example 4 (Update everything - form-data):**
```
video: [Binary file: updated-video.mp4]
poster: [Binary file: updated-poster.jpg]
title: "Complete Match Highlights Package"
category: "MATCHES"
duration_seconds: 180
sort_order: 1
is_active: true
```

**Response Example (200 OK):**
```json
{
  "status": "success",
  "message": "Gallery video updated successfully.",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440101",
    "key": "facility_tour",
    "video_url": "https://res.cloudinary.com/demo/video/upload/v1726086900/cms/gallery/videos/updated-video.mp4",
    "poster_url": "https://res.cloudinary.com/demo/image/upload/v1726086900/cms/gallery/posters/updated-poster.jpg",
    "title": "Complete Match Highlights Package",
    "category": "MATCHES",
    "duration_seconds": 180,
    "sort_order": 1,
    "is_active": true,
    "created_at": "2026-09-05T11:00:00Z",
    "updated_at": "2026-09-10T20:48:20Z"
  }
}
```

**cURL Example (Update metadata):**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/gallery/videos/660e8400-e29b-41d4-a716-446655440101/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "title": "Updated Match Highlights",
    "duration_seconds": 140
  }'
```

**cURL Example (Replace video):**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/gallery/videos/660e8400-e29b-41d4-a716-446655440101/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "video=@/path/to/new-video.mp4" \
  -F "title=New Match Highlights"
```

**JavaScript Example:**
```javascript
// Update metadata only
const response = await fetch(`/api/v1/cms/gallery/videos/${videoId}/`, {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${adminToken}`
  },
  body: JSON.stringify({
    title: 'Updated Title',
    duration_seconds: 140
  })
});

// Replace video and poster
const formData = new FormData();
formData.append('video', newVideoFile);
formData.append('poster', newPosterFile);
formData.append('title', 'Updated Video');

const response = await fetch(`/api/v1/cms/gallery/videos/${videoId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  },
  body: formData
});
```

**Use Case:** Admin editing video metadata or replacing video/poster files

---

### 🔴 DELETE - Delete Gallery Video

**Endpoint:**
```
DELETE /api/v1/cms/gallery/videos/{id}/
```

**Authentication:** Required (Admin only)

**Description:** Deletes the video from database and removes both video and poster files from Cloudinary.

**Request Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/cms/gallery/videos/660e8400-e29b-41d4-a716-446655440101/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Response Example (200 OK):**
```json
{
  "status": "success",
  "message": "Gallery video deleted successfully.",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440101",
    "title": "Complete Facility Tour"
  }
}
```

**JavaScript Example:**
```javascript
const confirmed = confirm('Are you sure you want to delete this video? This will also delete the poster image.');
if (!confirmed) return;

const response = await fetch(`/api/v1/cms/gallery/videos/${videoId}/`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  }
});

const result = await response.json();
if (result.status === 'success') {
  // Remove from UI
  removeVideoFromDOM(videoId);
}
```

**Use Case:** Admin deleting unwanted videos

---

## Complete Integration Workflows

### Workflow 1: Public Gallery Page

**Scenario:** Display gallery page to public visitors

**Steps:**
1. Fetch complete gallery data
2. Render header and categories
3. Render photos in masonry grid
4. Render videos section
5. Render CTA

**Code:**
```javascript
async function loadGalleryPage() {
  try {
    const response = await fetch('/api/v1/cms/gallery/');
    const { data } = await response.json();
    
    // Render header
    document.getElementById('gallery-eyebrow').textContent = data.header.eyebrow;
    document.getElementById('gallery-title').textContent = data.header.title;
    document.getElementById('gallery-description').textContent = data.header.description;
    
    // Render category filters
    const categoriesHTML = data.categories.map(cat => `
      <button class="category-btn" data-category="${cat.key}">
        ${cat.label}
      </button>
    `).join('');
    document.getElementById('categories').innerHTML = categoriesHTML;
    
    // Render photos
    const photosHTML = data.photos.map(photo => `
      <div class="photo-card" data-category="${photo.category}" style="aspect-ratio: ${photo.aspect_ratio}">
        <img src="${photo.url}" alt="${photo.alt_text}" title="${photo.title}" loading="lazy" />
      </div>
    `).join('');
    document.getElementById('photos-grid').innerHTML = photosHTML;
    
    // Render videos section
    document.getElementById('videos-heading').textContent = data.videos_section.heading;
    document.getElementById('videos-description').textContent = data.videos_section.description;
    
    const videosHTML = data.videos_section.videos.map(video => `
      <div class="video-card" data-category="${video.category}">
        <video controls poster="${video.poster}">
          <source src="${video.url}" type="video/mp4">
        </video>
        <h3>${video.title}</h3>
        <span class="duration">${formatDuration(video.duration_seconds)}</span>
      </div>
    `).join('');
    document.getElementById('videos-grid').innerHTML = videosHTML;
    
    // Render CTA
    document.getElementById('cta-heading').textContent = data.cta.heading;
    document.getElementById('cta-description').textContent = data.cta.description;
    document.getElementById('cta-button').textContent = data.cta.button.label;
    document.getElementById('cta-button').href = data.cta.button.href;
    
  } catch (error) {
    console.error('Failed to load gallery:', error);
  }
}

function formatDuration(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Load on page load
loadGalleryPage();

// Add category filtering
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('category-btn')) {
    const category = e.target.dataset.category;
    filterByCategory(category);
  }
});

function filterByCategory(category) {
  const photos = document.querySelectorAll('.photo-card');
  const videos = document.querySelectorAll('.video-card');
  
  photos.forEach(photo => {
    if (category === 'ALL' || photo.dataset.category === category) {
      photo.style.display = 'block';
    } else {
      photo.style.display = 'none';
    }
  });
  
  videos.forEach(video => {
    if (category === 'ALL' || video.dataset.category === category) {
      video.style.display = 'block';
    } else {
      video.style.display = 'none';
    }
  });
}
```

---

### Workflow 2: Admin - Update Page Text

**Scenario:** Admin edits gallery page headers and descriptions

**Steps:**
1. Fetch current gallery data
2. Pre-fill form with current values
3. Admin edits fields
4. Submit PATCH with changed fields only
5. Show success message
6. Refresh data

**Code:**
```javascript
// 1. Load current data into form
async function loadGalleryEditor() {
  const response = await fetch('/api/v1/cms/gallery/');
  const { data } = await response.json();
  
  // Pre-fill form
  document.getElementById('meta-title').value = data.meta_title;
  document.getElementById('meta-description').value = data.meta_description;
  document.getElementById('header-eyebrow').value = data.header.eyebrow;
  document.getElementById('header-title').value = data.header.title;
  document.getElementById('header-description').value = data.header.description;
  document.getElementById('videos-heading').value = data.videos_section.heading;
  document.getElementById('videos-description').value = data.videos_section.description;
  document.getElementById('cta-heading').value = data.cta.heading;
  document.getElementById('cta-description').value = data.cta.description;
  document.getElementById('cta-button-label').value = data.cta.button.label;
}

// 2. Handle form submission
document.getElementById('gallery-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  // Get changed fields only (optional optimization)
  const updates = {
    meta_title: document.getElementById('meta-title').value,
    meta_description: document.getElementById('meta-description').value,
    header_eyebrow: document.getElementById('header-eyebrow').value,
    header_title: document.getElementById('header-title').value,
    header_description: document.getElementById('header-description').value,
    videos_section_heading: document.getElementById('videos-heading').value,
    videos_section_description: document.getElementById('videos-description').value,
    cta_heading: document.getElementById('cta-heading').value,
    cta_description: document.getElementById('cta-description').value,
    cta_button_label: document.getElementById('cta-button-label').value
  };
  
  try {
    const response = await fetch('/api/v1/cms/gallery/', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAdminToken()}`
      },
      body: JSON.stringify(updates)
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      showSuccessMessage('Gallery page updated successfully!');
      loadGalleryEditor(); // Refresh data
    } else {
      showErrorMessage('Failed to update gallery page');
    }
  } catch (error) {
    console.error('Error updating gallery:', error);
    showErrorMessage('An error occurred');
  }
});

// Load editor on page load
loadGalleryEditor();
```

---

### Workflow 3: Admin - Upload Photo

**Scenario:** Admin uploads a new photo to the gallery

**Steps:**
1. Select image file
2. Fill in metadata (title, alt text, category, etc.)
3. Submit upload
4. Show upload progress (optional)
5. Display success and refresh gallery

**Code:**
```javascript
document.getElementById('photo-upload-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const fileInput = document.getElementById('photo-file');
  const file = fileInput.files[0];
  
  if (!file) {
    alert('Please select an image file');
    return;
  }
  
  // Create form data
  const formData = new FormData();
  formData.append('image', file);
  formData.append('title', document.getElementById('photo-title').value);
  formData.append('alt_text', document.getElementById('photo-alt-text').value);
  formData.append('category', document.getElementById('photo-category').value);
  formData.append('aspect_ratio', document.getElementById('photo-aspect-ratio').value);
  formData.append('sort_order', document.getElementById('photo-sort-order').value || '0');
  formData.append('is_active', 'true');
  
  try {
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Uploading...';
    
    const response = await fetch('/api/v1/cms/gallery/photos/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getAdminToken()}`
      },
      body: formData
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      showSuccessMessage(`Photo "${result.data.title}" uploaded successfully!`);
      
      // Reset form
      e.target.reset();
      
      // Refresh photo list
      loadPhotos();
    } else {
      showErrorMessage('Failed to upload photo');
    }
  } catch (error) {
    console.error('Error uploading photo:', error);
    showErrorMessage('An error occurred during upload');
  } finally {
    // Reset button state
    submitBtn.disabled = false;
    submitBtn.textContent = 'Upload Photo';
  }
});
```

---

### Workflow 4: Admin - Manage Photos List

**Scenario:** Admin views, edits, and deletes photos

**Steps:**
1. Fetch all photos
2. Display in admin UI
3. Allow edit/delete actions

**Code:**
```javascript
// Load all photos
async function loadPhotos(category = null) {
  try {
    let url = '/api/v1/cms/gallery/photos/?ordering=sort_order';
    if (category) url += `&category=${category}`;
    
    const response = await fetch(url);
    const { data: photos } = await response.json();
    
    const photosHTML = photos.map(photo => `
      <div class="admin-photo-card" data-id="${photo.id}">
        <img src="${photo.image_url}" alt="${photo.alt_text}" />
        <div class="photo-info">
          <h4>${photo.title}</h4>
          <p><strong>Category:</strong> ${photo.category}</p>
          <p><strong>Aspect Ratio:</strong> ${photo.aspect_ratio}</p>
          <p><strong>Sort Order:</strong> ${photo.sort_order}</p>
          <p><strong>Active:</strong> ${photo.is_active ? 'Yes' : 'No'}</p>
        </div>
        <div class="photo-actions">
          <button onclick="editPhoto('${photo.id}')" class="btn-edit">✏️ Edit</button>
          <button onclick="deletePhoto('${photo.id}', '${photo.title}')" class="btn-delete">🗑️ Delete</button>
        </div>
      </div>
    `).join('');
    
    document.getElementById('photos-list').innerHTML = photosHTML;
    document.getElementById('photos-count').textContent = `${photos.length} photos`;
    
  } catch (error) {
    console.error('Error loading photos:', error);
  }
}

// Delete photo
async function deletePhoto(photoId, photoTitle) {
  const confirmed = confirm(`Are you sure you want to delete "${photoTitle}"?`);
  if (!confirmed) return;
  
  try {
    const response = await fetch(`/api/v1/cms/gallery/photos/${photoId}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${getAdminToken()}`
      }
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      showSuccessMessage(`Photo "${photoTitle}" deleted successfully!`);
      loadPhotos(); // Refresh list
    } else {
      showErrorMessage('Failed to delete photo');
    }
  } catch (error) {
    console.error('Error deleting photo:', error);
    showErrorMessage('An error occurred');
  }
}

// Edit photo (open modal with photo data)
async function editPhoto(photoId) {
  try {
    const response = await fetch(`/api/v1/cms/gallery/photos/${photoId}/`);
    const { data: photo } = await response.json();
    
    // Open edit modal and pre-fill
    document.getElementById('edit-photo-id').value = photo.id;
    document.getElementById('edit-photo-title').value = photo.title;
    document.getElementById('edit-photo-alt-text').value = photo.alt_text;
    document.getElementById('edit-photo-category').value = photo.category;
    document.getElementById('edit-photo-aspect-ratio').value = photo.aspect_ratio;
    document.getElementById('edit-photo-sort-order').value = photo.sort_order;
    document.getElementById('edit-photo-is-active').checked = photo.is_active;
    document.getElementById('edit-photo-preview').src = photo.image_url;
    
    // Show modal
    document.getElementById('edit-photo-modal').classList.add('show');
    
  } catch (error) {
    console.error('Error loading photo:', error);
  }
}

// Save photo edits
document.getElementById('edit-photo-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const photoId = document.getElementById('edit-photo-id').value;
  const updates = {
    title: document.getElementById('edit-photo-title').value,
    alt_text: document.getElementById('edit-photo-alt-text').value,
    category: document.getElementById('edit-photo-category').value,
    aspect_ratio: document.getElementById('edit-photo-aspect-ratio').value,
    sort_order: parseInt(document.getElementById('edit-photo-sort-order').value),
    is_active: document.getElementById('edit-photo-is-active').checked
  };
  
  // If new image selected, use FormData
  const newImageFile = document.getElementById('edit-photo-file').files[0];
  let body, headers;
  
  if (newImageFile) {
    const formData = new FormData();
    formData.append('image', newImageFile);
    Object.keys(updates).forEach(key => {
      formData.append(key, updates[key]);
    });
    body = formData;
    headers = { 'Authorization': `Bearer ${getAdminToken()}` };
  } else {
    body = JSON.stringify(updates);
    headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAdminToken()}`
    };
  }
  
  try {
    const response = await fetch(`/api/v1/cms/gallery/photos/${photoId}/`, {
      method: 'PATCH',
      headers,
      body
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      showSuccessMessage('Photo updated successfully!');
      document.getElementById('edit-photo-modal').classList.remove('show');
      loadPhotos(); // Refresh list
    } else {
      showErrorMessage('Failed to update photo');
    }
  } catch (error) {
    console.error('Error updating photo:', error);
    showErrorMessage('An error occurred');
  }
});

// Load photos on page load
loadPhotos();
```

---

### Workflow 5: Admin - Upload Video

**Scenario:** Admin uploads a new video with poster to the gallery

**Code:**
```javascript
document.getElementById('video-upload-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const videoFile = document.getElementById('video-file').files[0];
  const posterFile = document.getElementById('video-poster-file').files[0];
  
  if (!videoFile || !posterFile) {
    alert('Please select both video file and poster image');
    return;
  }
  
  // Create form data
  const formData = new FormData();
  formData.append('video', videoFile);
  formData.append('poster', posterFile);
  formData.append('title', document.getElementById('video-title').value);
  formData.append('category', document.getElementById('video-category').value);
  formData.append('duration_seconds', document.getElementById('video-duration').value);
  formData.append('sort_order', document.getElementById('video-sort-order').value || '0');
  formData.append('is_active', 'true');
  
  try {
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Uploading...';
    
    const response = await fetch('/api/v1/cms/gallery/videos/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getAdminToken()}`
      },
      body: formData
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      showSuccessMessage(`Video "${result.data.title}" uploaded successfully!`);
      e.target.reset();
      loadVideos();
    } else {
      showErrorMessage('Failed to upload video');
    }
  } catch (error) {
    console.error('Error uploading video:', error);
    showErrorMessage('An error occurred during upload');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Upload Video';
  }
});
```

---

## Frontend Examples

### React Component - Gallery Page

```jsx
import { useEffect, useState } from 'react';

function GalleryPage() {
  const [galleryData, setGalleryData] = useState(null);
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadGallery();
  }, []);
  
  const loadGallery = async () => {
    try {
      const response = await fetch('/api/v1/cms/gallery/');
      const { data } = await response.json();
      setGalleryData(data);
    } catch (error) {
      console.error('Failed to load gallery:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const filteredPhotos = galleryData?.photos.filter(photo => 
    activeCategory === 'ALL' || photo.category === activeCategory
  ) || [];
  
  const filteredVideos = galleryData?.videos_section.videos.filter(video => 
    activeCategory === 'ALL' || video.category === activeCategory
  ) || [];
  
  if (loading) return <div>Loading gallery...</div>;
  if (!galleryData) return <div>Failed to load gallery</div>;
  
  return (
    <div className="gallery-page">
      {/* Header */}
      <header className="gallery-header">
        <span className="eyebrow">{galleryData.header.eyebrow}</span>
        <h1>{galleryData.header.title}</h1>
        <p>{galleryData.header.description}</p>
      </header>
      
      {/* Category filters */}
      <div className="category-filters">
        {galleryData.categories.map(category => (
          <button
            key={category.key}
            className={activeCategory === category.key ? 'active' : ''}
            onClick={() => setActiveCategory(category.key)}
          >
            {category.label}
          </button>
        ))}
      </div>
      
      {/* Photos grid */}
      <div className="photos-grid">
        {filteredPhotos.map(photo => (
          <div 
            key={photo.key} 
            className="photo-card"
            style={{ aspectRatio: photo.aspect_ratio }}
          >
            <img 
              src={photo.url} 
              alt={photo.alt_text} 
              title={photo.title}
              loading="lazy"
            />
          </div>
        ))}
      </div>
      
      {/* Videos section */}
      {filteredVideos.length > 0 && (
        <section className="videos-section">
          <h2>{galleryData.videos_section.heading}</h2>
          <p>{galleryData.videos_section.description}</p>
          
          <div className="videos-grid">
            {filteredVideos.map(video => (
              <div key={video.key} className="video-card">
                <video controls poster={video.poster}>
                  <source src={video.url} type="video/mp4" />
                </video>
                <h3>{video.title}</h3>
                <span className="duration">
                  {Math.floor(video.duration_seconds / 60)}:
                  {(video.duration_seconds % 60).toString().padStart(2, '0')}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}
      
      {/* CTA */}
      <section className="gallery-cta">
        <h2>{galleryData.cta.heading}</h2>
        <p>{galleryData.cta.description}</p>
        <a href={galleryData.cta.button.href} className="btn btn-primary">
          {galleryData.cta.button.label}
        </a>
      </section>
    </div>
  );
}

export default GalleryPage;
```

---

### React Component - Admin Photo Upload

```jsx
import { useState } from 'react';

function PhotoUploadForm({ onSuccess }) {
  const [formData, setFormData] = useState({
    title: '',
    alt_text: '',
    category: 'VENUE',
    aspect_ratio: '4/3',
    sort_order: 0
  });
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      alert('Please select an image');
      return;
    }
    
    const data = new FormData();
    data.append('image', file);
    data.append('title', formData.title);
    data.append('alt_text', formData.alt_text);
    data.append('category', formData.category);
    data.append('aspect_ratio', formData.aspect_ratio);
    data.append('sort_order', formData.sort_order);
    data.append('is_active', 'true');
    
    setUploading(true);
    
    try {
      const response = await fetch('/api/v1/cms/gallery/photos/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: data
      });
      
      const result = await response.json();
      
      if (result.status === 'success') {
        alert('Photo uploaded successfully!');
        onSuccess(result.data);
        // Reset form
        setFormData({
          title: '',
          alt_text: '',
          category: 'VENUE',
          aspect_ratio: '4/3',
          sort_order: 0
        });
        setFile(null);
      } else {
        alert('Upload failed');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred');
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="photo-upload-form">
      <h3>Upload New Photo</h3>
      
      <div className="form-group">
        <label>Image File *</label>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files[0])}
          required
        />
      </div>
      
      <div className="form-group">
        <label>Title *</label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({...formData, title: e.target.value})}
          required
          maxLength={200}
        />
      </div>
      
      <div className="form-group">
        <label>Alt Text (for accessibility) *</label>
        <input
          type="text"
          value={formData.alt_text}
          onChange={(e) => setFormData({...formData, alt_text: e.target.value})}
          required
          maxLength={200}
        />
      </div>
      
      <div className="form-group">
        <label>Category *</label>
        <select
          value={formData.category}
          onChange={(e) => setFormData({...formData, category: e.target.value})}
          required
        >
          <option value="VENUE">Venue & Facilities</option>
          <option value="MATCHES">Match Action</option>
          <option value="COMMUNITY">Community & Events</option>
        </select>
      </div>
      
      <div className="form-group">
        <label>Aspect Ratio</label>
        <select
          value={formData.aspect_ratio}
          onChange={(e) => setFormData({...formData, aspect_ratio: e.target.value})}
        >
          <option value="16/10">16:10 (Wide Landscape)</option>
          <option value="16/9">16:9 (Standard Wide)</option>
          <option value="4/3">4:3 (Traditional)</option>
          <option value="1/1">1:1 (Square)</option>
          <option value="3/4">3:4 (Portrait)</option>
        </select>
      </div>
      
      <div className="form-group">
        <label>Sort Order</label>
        <input
          type="number"
          value={formData.sort_order}
          onChange={(e) => setFormData({...formData, sort_order: parseInt(e.target.value)})}
          min="0"
        />
      </div>
      
      <button type="submit" disabled={uploading} className="btn btn-primary">
        {uploading ? 'Uploading...' : 'Upload Photo'}
      </button>
    </form>
  );
}

export default PhotoUploadForm;
```

---

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "title": ["This field is required."],
    "category": ["Invalid category. Must be one of: VENUE, MATCHES, COMMUNITY"]
  }
}
```

### 401 Unauthorized
```json
{
  "status": "error",
  "message": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "status": "error",
  "message": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "status": "error",
  "message": "Not found."
}
```

---

## Testing with Swagger

Access Swagger UI at: `http://localhost:8000/api/v1/docs/`

1. Navigate to **"cms"** tag
2. Find **"Gallery"** endpoints
3. Click **"Try it out"** on any endpoint
4. Fill in parameters/body
5. Click **"Execute"**
6. View response

---

## Summary

✅ **3 independent systems** (page content, photos, videos)  
✅ **Public GET** returns everything in one response  
✅ **Admin PATCH** updates page text only  
✅ **Media APIs** handle file uploads/updates/deletes  
✅ **Automatic cache invalidation** keeps data fresh  
✅ **Cloudinary integration** for file storage  
✅ **Category filtering** (VENUE, MATCHES, COMMUNITY)  
✅ **Full CRUD** for photos and videos  

**This guide contains everything needed to integrate the Gallery CMS!** 🚀
