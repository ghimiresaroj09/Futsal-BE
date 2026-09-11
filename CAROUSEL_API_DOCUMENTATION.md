# Carousel API Documentation

## Overview

Complete REST API for managing homepage carousel images with full CRUD operations, image uploads to Cloudinary, and public/admin access control.

**Base URL:** `/api/v1/cms/homepage/carousel/`

**Date Created:** September 11, 2026

---

## Features

✅ **Full CRUD operations** (Create, Read, Update, Delete)  
✅ **Image upload** to Cloudinary  
✅ **Public read access** (view carousel images)  
✅ **Admin-only write access** (create/update/delete)  
✅ **Active/inactive toggle** (show/hide images)  
✅ **Sort ordering** for display control  
✅ **Alt text** for accessibility  
✅ **Automatic timestamps**  
✅ **Swagger documentation**  

---

## Database Model

```python
class CarouselImage:
    id: UUID (auto-generated)
    image: ImageField (stored in Cloudinary)
    alt_text: CharField(max_length=200)
    sort_order: IntegerField (default=0)
    is_active: BooleanField (default=True)
    created_at: DateTime (auto)
    updated_at: DateTime (auto)
```

---

## API Endpoints

### 🔵 GET - List All Carousel Images

**Endpoint:**
```
GET /api/v1/cms/homepage/carousel/
```

**Authentication:** None (Public)

**Description:** Returns all active carousel images. Admins see all images (including inactive).

**Query Parameters:**
- `is_active` (optional): Filter by active status (true, false)
- `ordering` (optional): Sort results (sort_order, -sort_order, created_at, -created_at)

**Request Example:**
```bash
# Get all active carousel images
curl -X GET "http://localhost:8000/api/v1/cms/homepage/carousel/"

# Filter for inactive images (admin only)
curl -X GET "http://localhost:8000/api/v1/cms/homepage/carousel/?is_active=false" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Sort by creation date (newest first)
curl -X GET "http://localhost:8000/api/v1/cms/homepage/carousel/?ordering=-created_at"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Carousel images retrieved successfully.",
  "data": {
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "650e8400-e29b-41d4-a716-446655440001",
        "image_url": "https://res.cloudinary.com/demo/image/upload/v1/carousel/slide-1.jpg",
        "alt_text": "Players in action during an intense futsal match",
        "sort_order": 1,
        "is_active": true,
        "created_at": "2026-09-05T10:00:00Z",
        "updated_at": "2026-09-05T10:00:00Z"
      },
      {
        "id": "650e8400-e29b-41d4-a716-446655440002",
        "image_url": "https://res.cloudinary.com/demo/image/upload/v1/carousel/slide-2.jpg",
        "alt_text": "Premium indoor futsal court with professional lighting",
        "sort_order": 2,
        "is_active": true,
        "created_at": "2026-09-06T14:30:00Z",
        "updated_at": "2026-09-06T14:30:00Z"
      },
      {
        "id": "650e8400-e29b-41d4-a716-446655440003",
        "image_url": "https://res.cloudinary.com/demo/image/upload/v1/carousel/slide-3.jpg",
        "alt_text": "Community tournament celebration moment",
        "sort_order": 3,
        "is_active": true,
        "created_at": "2026-09-07T16:00:00Z",
        "updated_at": "2026-09-07T16:00:00Z"
      }
    ]
  }
}
```

---

### 🟢 POST - Upload Carousel Image

**Endpoint:**
```
POST /api/v1/cms/homepage/carousel/
```

**Authentication:** Required (Admin only)

**Content-Type:** `multipart/form-data`

**Description:** Upload a new carousel image with alt text.

**Request Headers:**
```
Content-Type: multipart/form-data
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Request Body (form-data):**
```
image: [Binary file: slide-4.jpg] (required)
alt_text: "Award ceremony for tournament winners" (required)
sort_order: 4 (optional, default: 0)
is_active: true (optional, default: true)
```

**Full Field Reference:**
```
image (required): Image file (JPEG, PNG, WebP)
alt_text (required): Alt text for accessibility (max 200 chars)
sort_order (optional): Integer (default: 0) - lower numbers appear first
is_active (optional): Boolean (default: true)
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Carousel image uploaded successfully.",
  "data": {
    "id": "650e8400-e29b-41d4-a716-446655440010",
    "image_url": "https://res.cloudinary.com/demo/image/upload/v1726234567/carousel/slide-4.jpg",
    "alt_text": "Award ceremony for tournament winners",
    "sort_order": 4,
    "is_active": true,
    "created_at": "2026-09-11T16:52:00Z",
    "updated_at": "2026-09-11T16:52:00Z"
  }
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/cms/homepage/carousel/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "image=@/path/to/slide-4.jpg" \
  -F "alt_text=Award ceremony for tournament winners" \
  -F "sort_order=4" \
  -F "is_active=true"
```

**JavaScript Example:**
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('alt_text', 'Award ceremony for tournament winners');
formData.append('sort_order', '4');
formData.append('is_active', 'true');

const response = await fetch('/api/v1/cms/homepage/carousel/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  },
  body: formData
});

const result = await response.json();
console.log(result.data); // New carousel image data
```

---

### 🔵 GET - Get Single Carousel Image

**Endpoint:**
```
GET /api/v1/cms/homepage/carousel/{id}/
```

**Authentication:** None (Public)

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/cms/homepage/carousel/650e8400-e29b-41d4-a716-446655440001/"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "650e8400-e29b-41d4-a716-446655440001",
    "image_url": "https://res.cloudinary.com/demo/image/upload/v1/carousel/slide-1.jpg",
    "alt_text": "Players in action during an intense futsal match",
    "sort_order": 1,
    "is_active": true,
    "created_at": "2026-09-05T10:00:00Z",
    "updated_at": "2026-09-05T10:00:00Z"
  }
}
```

---

### 🟡 PATCH - Update Carousel Image

**Endpoint:**
```
PATCH /api/v1/cms/homepage/carousel/{id}/
```

**Authentication:** Required (Admin only)

**Content-Type:** `multipart/form-data` or `application/json`

**Description:** Update carousel image or metadata. Only include fields you want to change.

**Request Headers:**
```
Content-Type: multipart/form-data
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Request Body Example 1 (Update metadata only - JSON):**
```json
{
  "alt_text": "Updated description of the match scene",
  "sort_order": 1,
  "is_active": true
}
```

**Request Body Example 2 (Replace image - form-data):**
```
image: [Binary file: new-slide.jpg]
```

**Request Body Example 3 (Update multiple fields - form-data):**
```
alt_text: "New description"
sort_order: 5
is_active: true
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Carousel image updated successfully.",
  "data": {
    "id": "650e8400-e29b-41d4-a716-446655440001",
    "image_url": "https://res.cloudinary.com/demo/image/upload/v1726234800/carousel/new-slide.jpg",
    "alt_text": "New description",
    "sort_order": 5,
    "is_active": true,
    "created_at": "2026-09-05T10:00:00Z",
    "updated_at": "2026-09-11T16:55:00Z"
  }
}
```

**cURL Example (Update metadata):**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/homepage/carousel/650e8400-e29b-41d4-a716-446655440001/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "alt_text": "Updated description",
    "sort_order": 1
  }'
```

**cURL Example (Replace image):**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/homepage/carousel/650e8400-e29b-41d4-a716-446655440001/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "image=@/path/to/new-slide.jpg"
```

**JavaScript Example:**
```javascript
// Update metadata only
const response = await fetch(`/api/v1/cms/homepage/carousel/${imageId}/`, {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${adminToken}`
  },
  body: JSON.stringify({
    alt_text: 'Updated description',
    sort_order: 1
  })
});

// Replace image
const formData = new FormData();
formData.append('image', newFile);

const response = await fetch(`/api/v1/cms/homepage/carousel/${imageId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  },
  body: formData
});
```

---

### 🔴 DELETE - Delete Carousel Image

**Endpoint:**
```
DELETE /api/v1/cms/homepage/carousel/{id}/
```

**Authentication:** Required (Admin only)

**Description:** Deletes the carousel image from database and removes the image from Cloudinary.

**Request Headers:**
```
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Request Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/cms/homepage/carousel/650e8400-e29b-41d4-a716-446655440001/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Carousel image deleted successfully.",
  "data": {
    "id": "650e8400-e29b-41d4-a716-446655440001",
    "alt_text": "Players in action during an intense futsal match"
  }
}
```

**JavaScript Example:**
```javascript
const confirmed = confirm('Are you sure you want to delete this carousel image?');
if (!confirmed) return;

const response = await fetch(`/api/v1/cms/homepage/carousel/${imageId}/`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  }
});

const result = await response.json();
if (result.status === 'success') {
  // Remove from UI
  removeCarouselFromDOM(imageId);
}
```

---

## Frontend Integration

### React Example - Carousel Display

```jsx
import { useEffect, useState } from 'react';
import { Carousel } from 'react-responsive-carousel';
import 'react-responsive-carousel/lib/styles/carousel.min.css';

function HomepageCarousel() {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadCarousel();
  }, []);
  
  const loadCarousel = async () => {
    try {
      const response = await fetch('/api/v1/cms/homepage/carousel/?is_active=true&ordering=sort_order');
      const result = await response.json();
      setImages(result.data.results || []);
    } catch (error) {
      console.error('Failed to load carousel:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <div>Loading carousel...</div>;
  if (images.length === 0) return null;
  
  return (
    <Carousel
      autoPlay
      infiniteLoop
      interval={5000}
      showThumbs={false}
      showStatus={false}
    >
      {images.map(image => (
        <div key={image.id}>
          <img 
            src={image.image_url} 
            alt={image.alt_text}
            style={{
              maxHeight: '600px',
              objectFit: 'cover'
            }}
          />
        </div>
      ))}
    </Carousel>
  );
}

export default HomepageCarousel();
```

---

### React Example - Admin Upload Form

```jsx
import { useState } from 'react';

function CarouselUploadForm({ onSuccess }) {
  const [imageFile, setImageFile] = useState(null);
  const [altText, setAltText] = useState('');
  const [sortOrder, setSortOrder] = useState(0);
  const [uploading, setUploading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!imageFile) {
      alert('Please select an image');
      return;
    }
    
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('alt_text', altText);
    formData.append('sort_order', sortOrder);
    formData.append('is_active', 'true');
    
    setUploading(true);
    
    try {
      const response = await fetch('/api/v1/cms/homepage/carousel/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: formData
      });
      
      const result = await response.json();
      
      if (result.status === 'success') {
        alert('Carousel image uploaded successfully!');
        onSuccess(result.data);
        
        // Reset form
        setImageFile(null);
        setAltText('');
        setSortOrder(0);
      } else {
        alert('Failed to upload carousel image');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred');
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="carousel-upload-form">
      <h3>Upload Carousel Image</h3>
      
      <div className="form-group">
        <label>Image *</label>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setImageFile(e.target.files[0])}
          required
        />
      </div>
      
      <div className="form-group">
        <label>Alt Text (for accessibility) *</label>
        <input
          type="text"
          value={altText}
          onChange={(e) => setAltText(e.target.value)}
          placeholder="Describe the image for screen readers"
          required
          maxLength={200}
        />
      </div>
      
      <div className="form-group">
        <label>Sort Order</label>
        <input
          type="number"
          value={sortOrder}
          onChange={(e) => setSortOrder(parseInt(e.target.value))}
          min="0"
        />
        <small>Lower numbers appear first</small>
      </div>
      
      <button type="submit" disabled={uploading} className="btn btn-primary">
        {uploading ? 'Uploading...' : 'Upload Image'}
      </button>
    </form>
  );
}

export default CarouselUploadForm;
```

---

### JavaScript Example - Admin Management

```javascript
// Load all carousel images (admin view)
async function loadCarouselImages() {
  const response = await fetch('/api/v1/cms/homepage/carousel/', {
    headers: {
      'Authorization': `Bearer ${adminToken}`
    }
  });
  const result = await response.json();
  
  renderCarouselList(result.data.results);
}

// Delete carousel image
async function deleteCarouselImage(id, altText) {
  const confirmed = confirm(`Delete carousel image: ${altText}?`);
  if (!confirmed) return;
  
  try {
    const response = await fetch(`/api/v1/cms/homepage/carousel/${id}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${adminToken}`
      }
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      showSuccess('Carousel image deleted successfully');
      loadCarouselImages(); // Refresh list
    } else {
      showError('Failed to delete carousel image');
    }
  } catch (error) {
    console.error('Error:', error);
    showError('An error occurred');
  }
}

// Toggle active status
async function toggleCarouselActive(id, currentStatus) {
  try {
    const response = await fetch(`/api/v1/cms/homepage/carousel/${id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${adminToken}`
      },
      body: JSON.stringify({
        is_active: !currentStatus
      })
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      showSuccess(`Carousel image ${result.data.is_active ? 'activated' : 'deactivated'}`);
      loadCarouselImages();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Render carousel list in admin panel
function renderCarouselList(images) {
  const html = images.map(img => `
    <div class="carousel-item" data-id="${img.id}">
      <img src="${img.image_url}" alt="${img.alt_text}" class="thumbnail" />
      
      <div class="info">
        <p class="alt-text">${img.alt_text}</p>
        <span class="sort-order">Order: ${img.sort_order}</span>
        <span class="status ${img.is_active ? 'active' : 'inactive'}">
          ${img.is_active ? '✓ Active' : '✗ Inactive'}
        </span>
      </div>
      
      <div class="actions">
        <button onclick="editCarouselImage('${img.id}')" class="btn-edit">Edit</button>
        <button onclick="toggleCarouselActive('${img.id}', ${img.is_active})" class="btn-toggle">
          ${img.is_active ? 'Deactivate' : 'Activate'}
        </button>
        <button onclick="deleteCarouselImage('${img.id}', '${img.alt_text}')" class="btn-delete">Delete</button>
      </div>
    </div>
  `).join('');
  
  document.getElementById('carousel-list').innerHTML = html;
}
```

---

## Validation Rules

### Required Fields
- ✅ `image` - Required on create
- ✅ `alt_text` - Cannot be empty

### Optional Fields
- `sort_order` - Default: 0
- `is_active` - Default: true

### Field Constraints
- `alt_text`: Max 200 characters
- `sort_order`: Must be non-negative integer

---

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "alt_text": ["Alt text cannot be empty."],
    "image": ["This field is required."]
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
2. Find carousel endpoints
3. Click **"Try it out"** on any endpoint
4. For POST/PATCH/DELETE: Click "Authorize" and add your admin token
5. Fill in parameters/body
6. Click **"Execute"**
7. View response

---

## CSS Example for Carousel

```css
.carousel-container {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
}

.carousel-slide {
  width: 100%;
  height: 600px;
  object-fit: cover;
  display: none;
}

.carousel-slide.active {
  display: block;
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.carousel-controls {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
}

.carousel-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s;
}

.carousel-dot.active {
  background: white;
  transform: scale(1.2);
}

.carousel-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  padding: 20px;
  cursor: pointer;
  font-size: 24px;
  transition: background 0.3s;
}

.carousel-arrow:hover {
  background: rgba(0, 0, 0, 0.8);
}

.carousel-arrow.prev {
  left: 20px;
}

.carousel-arrow.next {
  right: 20px;
}
```

---

## Summary

✅ **CarouselImage model** created  
✅ **Full CRUD API** with ViewSet  
✅ **Image upload** to Cloudinary  
✅ **Public read access** (active images only)  
✅ **Admin write access** (create/update/delete)  
✅ **Sort ordering** for display control  
✅ **Alt text** for accessibility  
✅ **Active/inactive toggle**  
✅ **Django admin panel** integration  
✅ **Swagger documentation** included  
✅ **Migrations** created and applied  

**The Carousel API is ready to use!** 🚀

**Test it at:** `http://localhost:8000/api/v1/docs/` → Look for "cms" tag → "homepage/carousel"
