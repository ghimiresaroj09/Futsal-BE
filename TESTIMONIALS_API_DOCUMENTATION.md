# Testimonials API Documentation

## Overview

Complete REST API for managing customer testimonials with full CRUD operations, image uploads to Cloudinary, and public/admin access control.

**Base URL:** `/api/v1/cms/testimonials/`

**Date Created:** September 11, 2026

---

## Features

✅ **Full CRUD operations** (Create, Read, Update, Delete)  
✅ **Image upload** to Cloudinary  
✅ **Public read access** (view testimonials)  
✅ **Admin-only write access** (create/update/delete)  
✅ **Active/inactive toggle** (show/hide on website)  
✅ **Sort ordering** for display control  
✅ **Automatic timestamps** (created_at, updated_at)  
✅ **Swagger documentation** integrated  

---

## Database Model

```python
class Testimonial:
    id: UUID (auto-generated)
    full_name: CharField(max_length=200)
    title: CharField(max_length=200)  # e.g., "Regular Player", "Tournament Organizer"
    image: ImageField (optional, stored in Cloudinary)
    content: TextField
    is_active: BooleanField (default=True)
    sort_order: IntegerField (default=0)
    created_at: DateTime (auto)
    updated_at: DateTime (auto)
```

---

## API Endpoints

### 🔵 GET - List All Testimonials

**Endpoint:**
```
GET /api/v1/cms/testimonials/
```

**Authentication:** None (Public)

**Description:** Returns all active testimonials. Admins see all testimonials (including inactive).

**Query Parameters:**
- `is_active` (optional): Filter by active status (true, false)
- `ordering` (optional): Sort results (sort_order, -sort_order, created_at, -created_at)

**Request Example:**
```bash
# Get all active testimonials
curl -X GET "http://localhost:8000/api/v1/cms/testimonials/"

# Filter for inactive testimonials (admin only)
curl -X GET "http://localhost:8000/api/v1/cms/testimonials/?is_active=false" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Sort by creation date (newest first)
curl -X GET "http://localhost:8000/api/v1/cms/testimonials/?ordering=-created_at"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Testimonials retrieved successfully.",
  "data": {
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "full_name": "Rajesh Kumar",
        "title": "Regular Player",
        "image_url": "https://res.cloudinary.com/demo/image/upload/v1/testimonials/rajesh.jpg",
        "content": "Best futsal arena in the city! The turf quality is excellent and the staff is very professional. I've been playing here for 2 years and it's always a great experience.",
        "is_active": true,
        "sort_order": 1,
        "created_at": "2026-09-05T10:00:00Z",
        "updated_at": "2026-09-05T10:00:00Z"
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "full_name": "Priya Sharma",
        "title": "Tournament Organizer",
        "image_url": "https://res.cloudinary.com/demo/image/upload/v1/testimonials/priya.jpg",
        "content": "We organized our company tournament here and everything was perfect. Easy booking system, great facilities, and excellent customer support.",
        "is_active": true,
        "sort_order": 2,
        "created_at": "2026-09-06T14:30:00Z",
        "updated_at": "2026-09-06T14:30:00Z"
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "full_name": "Amit Thapa",
        "title": "Weekend Player",
        "image_url": null,
        "content": "Great place to play with friends on weekends. The online booking makes it super convenient. Highly recommended!",
        "is_active": true,
        "sort_order": 3,
        "created_at": "2026-09-07T16:00:00Z",
        "updated_at": "2026-09-07T16:00:00Z"
      }
    ]
  }
}
```

---

### 🟢 POST - Create New Testimonial

**Endpoint:**
```
POST /api/v1/cms/testimonials/
```

**Authentication:** Required (Admin only)

**Content-Type:** `multipart/form-data`

**Description:** Create a new testimonial with optional image upload.

**Request Headers:**
```
Content-Type: multipart/form-data
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Request Body (form-data):**
```
full_name: "Suman Rai" (required)
title: "Team Captain" (required)
content: "Amazing facility with top-notch equipment..." (required)
image: [Binary file: suman.jpg] (optional)
is_active: true (optional, default: true)
sort_order: 4 (optional, default: 0)
```

**Full Field Reference:**
```
full_name (required): Customer's full name (max 200 chars)
title (required): Job title or role (max 200 chars)
content (required): Testimonial text
image (optional): Image file (JPEG, PNG, WebP)
is_active (optional): Boolean (default: true)
sort_order (optional): Integer (default: 0) - lower numbers appear first
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Testimonial created successfully.",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440010",
    "full_name": "Suman Rai",
    "title": "Team Captain",
    "image_url": "https://res.cloudinary.com/demo/image/upload/v1726234567/testimonials/suman.jpg",
    "content": "Amazing facility with top-notch equipment. We play here every weekend and it never disappoints. The booking system is easy to use and the staff is friendly.",
    "is_active": true,
    "sort_order": 4,
    "created_at": "2026-09-11T16:30:00Z",
    "updated_at": "2026-09-11T16:30:00Z"
  }
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/cms/testimonials/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "full_name=Suman Rai" \
  -F "title=Team Captain" \
  -F "content=Amazing facility with top-notch equipment..." \
  -F "image=@/path/to/suman.jpg" \
  -F "is_active=true" \
  -F "sort_order=4"
```

**JavaScript Example:**
```javascript
const formData = new FormData();
formData.append('full_name', 'Suman Rai');
formData.append('title', 'Team Captain');
formData.append('content', 'Amazing facility with top-notch equipment...');
formData.append('image', fileInput.files[0]);
formData.append('is_active', 'true');
formData.append('sort_order', '4');

const response = await fetch('/api/v1/cms/testimonials/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  },
  body: formData
});

const result = await response.json();
console.log(result.data); // New testimonial data
```

---

### 🔵 GET - Get Single Testimonial

**Endpoint:**
```
GET /api/v1/cms/testimonials/{id}/
```

**Authentication:** None (Public)

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/cms/testimonials/550e8400-e29b-41d4-a716-446655440001/"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "full_name": "Rajesh Kumar",
    "title": "Regular Player",
    "image_url": "https://res.cloudinary.com/demo/image/upload/v1/testimonials/rajesh.jpg",
    "content": "Best futsal arena in the city!...",
    "is_active": true,
    "sort_order": 1,
    "created_at": "2026-09-05T10:00:00Z",
    "updated_at": "2026-09-05T10:00:00Z"
  }
}
```

---

### 🟡 PATCH - Update Testimonial

**Endpoint:**
```
PATCH /api/v1/cms/testimonials/{id}/
```

**Authentication:** Required (Admin only)

**Content-Type:** `multipart/form-data` or `application/json`

**Description:** Update testimonial details or replace the image. Only include fields you want to change.

**Request Headers:**
```
Content-Type: multipart/form-data
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Request Body Example 1 (Update text only - JSON):**
```json
{
  "full_name": "Rajesh Kumar Sharma",
  "title": "Senior Player",
  "content": "Updated review content...",
  "is_active": true,
  "sort_order": 1
}
```

**Request Body Example 2 (Replace image - form-data):**
```
image: [Binary file: new-photo.jpg]
```

**Request Body Example 3 (Update multiple fields - form-data):**
```
full_name: "Rajesh Kumar Sharma"
title: "Senior Player & Coach"
content: "Updated detailed review..."
image: [Binary file: updated-photo.jpg]
is_active: true
sort_order: 1
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Testimonial updated successfully.",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "full_name": "Rajesh Kumar Sharma",
    "title": "Senior Player & Coach",
    "image_url": "https://res.cloudinary.com/demo/image/upload/v1726234800/testimonials/updated-photo.jpg",
    "content": "Updated detailed review...",
    "is_active": true,
    "sort_order": 1,
    "created_at": "2026-09-05T10:00:00Z",
    "updated_at": "2026-09-11T16:35:00Z"
  }
}
```

**cURL Example (Update metadata):**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/testimonials/550e8400-e29b-41d4-a716-446655440001/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "full_name": "Rajesh Kumar Sharma",
    "title": "Senior Player",
    "sort_order": 1
  }'
```

**cURL Example (Replace image):**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/testimonials/550e8400-e29b-41d4-a716-446655440001/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "image=@/path/to/new-photo.jpg"
```

**JavaScript Example:**
```javascript
// Update metadata only
const response = await fetch(`/api/v1/cms/testimonials/${testimonialId}/`, {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${adminToken}`
  },
  body: JSON.stringify({
    title: 'Senior Player & Coach',
    sort_order: 1
  })
});

// Replace image
const formData = new FormData();
formData.append('image', newFile);

const response = await fetch(`/api/v1/cms/testimonials/${testimonialId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  },
  body: formData
});
```

---

### 🔴 DELETE - Delete Testimonial

**Endpoint:**
```
DELETE /api/v1/cms/testimonials/{id}/
```

**Authentication:** Required (Admin only)

**Description:** Deletes the testimonial from database and removes the image from Cloudinary.

**Request Headers:**
```
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Request Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/cms/testimonials/550e8400-e29b-41d4-a716-446655440001/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Testimonial deleted successfully.",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "full_name": "Rajesh Kumar"
  }
}
```

**JavaScript Example:**
```javascript
const confirmed = confirm('Are you sure you want to delete this testimonial?');
if (!confirmed) return;

const response = await fetch(`/api/v1/cms/testimonials/${testimonialId}/`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${adminToken}`
  }
});

const result = await response.json();
if (result.status === 'success') {
  // Remove from UI
  removeTestimonialFromDOM(testimonialId);
}
```

---

## Frontend Integration

### React Example - Testimonials List

```jsx
import { useEffect, useState } from 'react';

function TestimonialsList() {
  const [testimonials, setTestimonials] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadTestimonials();
  }, []);
  
  const loadTestimonials = async () => {
    try {
      const response = await fetch('/api/v1/cms/testimonials/?is_active=true&ordering=sort_order');
      const result = await response.json();
      setTestimonials(result.data.results || []);
    } catch (error) {
      console.error('Failed to load testimonials:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <div>Loading testimonials...</div>;
  
  return (
    <div className="testimonials-section">
      <h2>What Our Customers Say</h2>
      
      <div className="testimonials-grid">
        {testimonials.map(testimonial => (
          <div key={testimonial.id} className="testimonial-card">
            {testimonial.image_url && (
              <img 
                src={testimonial.image_url} 
                alt={testimonial.full_name}
                className="testimonial-avatar"
              />
            )}
            
            <div className="testimonial-content">
              <p className="quote">"{testimonial.content}"</p>
              
              <div className="author">
                <strong>{testimonial.full_name}</strong>
                <span className="title">{testimonial.title}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TestimonialsList;
```

---

### React Example - Admin Create Form

```jsx
import { useState } from 'react';

function TestimonialCreateForm({ onSuccess }) {
  const [formData, setFormData] = useState({
    full_name: '',
    title: '',
    content: '',
    is_active: true,
    sort_order: 0
  });
  const [imageFile, setImageFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const data = new FormData();
    data.append('full_name', formData.full_name);
    data.append('title', formData.title);
    data.append('content', formData.content);
    data.append('is_active', formData.is_active);
    data.append('sort_order', formData.sort_order);
    
    if (imageFile) {
      data.append('image', imageFile);
    }
    
    setUploading(true);
    
    try {
      const response = await fetch('/api/v1/cms/testimonials/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: data
      });
      
      const result = await response.json();
      
      if (result.status === 'success') {
        alert('Testimonial created successfully!');
        onSuccess(result.data);
        
        // Reset form
        setFormData({
          full_name: '',
          title: '',
          content: '',
          is_active: true,
          sort_order: 0
        });
        setImageFile(null);
      } else {
        alert('Failed to create testimonial');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred');
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="testimonial-form">
      <h3>Add New Testimonial</h3>
      
      <div className="form-group">
        <label>Full Name *</label>
        <input
          type="text"
          value={formData.full_name}
          onChange={(e) => setFormData({...formData, full_name: e.target.value})}
          required
          maxLength={200}
        />
      </div>
      
      <div className="form-group">
        <label>Title *</label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({...formData, title: e.target.value})}
          placeholder="e.g., Regular Player, Team Captain"
          required
          maxLength={200}
        />
      </div>
      
      <div className="form-group">
        <label>Content *</label>
        <textarea
          value={formData.content}
          onChange={(e) => setFormData({...formData, content: e.target.value})}
          required
          rows={5}
        />
      </div>
      
      <div className="form-group">
        <label>Image (optional)</label>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setImageFile(e.target.files[0])}
        />
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
      
      <div className="form-group checkbox">
        <label>
          <input
            type="checkbox"
            checked={formData.is_active}
            onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
          />
          Active (show on website)
        </label>
      </div>
      
      <button type="submit" disabled={uploading} className="btn btn-primary">
        {uploading ? 'Creating...' : 'Create Testimonial'}
      </button>
    </form>
  );
}

export default TestimonialCreateForm;
```

---

### JavaScript Example - Admin Management

```javascript
// Load all testimonials (admin view - includes inactive)
async function loadTestimonials() {
  const response = await fetch('/api/v1/cms/testimonials/', {
    headers: {
      'Authorization': `Bearer ${adminToken}`
    }
  });
  const result = await response.json();
  
  renderTestimonials(result.data.results);
}

// Delete testimonial
async function deleteTestimonial(id, fullName) {
  const confirmed = confirm(`Delete testimonial from ${fullName}?`);
  if (!confirmed) return;
  
  try {
    const response = await fetch(`/api/v1/cms/testimonials/${id}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${adminToken}`
      }
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      showSuccess('Testimonial deleted successfully');
      loadTestimonials(); // Refresh list
    } else {
      showError('Failed to delete testimonial');
    }
  } catch (error) {
    console.error('Error:', error);
    showError('An error occurred');
  }
}

// Toggle active status
async function toggleActive(id, currentStatus) {
  try {
    const response = await fetch(`/api/v1/cms/testimonials/${id}/`, {
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
      showSuccess(`Testimonial ${result.data.is_active ? 'activated' : 'deactivated'}`);
      loadTestimonials();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Render testimonials in admin panel
function renderTestimonials(testimonials) {
  const html = testimonials.map(t => `
    <div class="testimonial-item" data-id="${t.id}">
      <div class="testimonial-header">
        ${t.image_url ? `<img src="${t.image_url}" alt="${t.full_name}" />` : '<div class="no-image">No Image</div>'}
        <div class="info">
          <strong>${t.full_name}</strong>
          <span class="title">${t.title}</span>
        </div>
      </div>
      
      <p class="content">${t.content}</p>
      
      <div class="meta">
        <span class="status ${t.is_active ? 'active' : 'inactive'}">
          ${t.is_active ? '✓ Active' : '✗ Inactive'}
        </span>
        <span class="sort-order">Order: ${t.sort_order}</span>
      </div>
      
      <div class="actions">
        <button onclick="editTestimonial('${t.id}')" class="btn-edit">Edit</button>
        <button onclick="toggleActive('${t.id}', ${t.is_active})" class="btn-toggle">
          ${t.is_active ? 'Deactivate' : 'Activate'}
        </button>
        <button onclick="deleteTestimonial('${t.id}', '${t.full_name}')" class="btn-delete">Delete</button>
      </div>
    </div>
  `).join('');
  
  document.getElementById('testimonials-list').innerHTML = html;
}
```

---

## Validation Rules

### Required Fields
- ✅ `full_name` - Cannot be empty
- ✅ `title` - Cannot be empty
- ✅ `content` - Cannot be empty

### Optional Fields
- `image` - Image file (JPEG, PNG, WebP)
- `is_active` - Default: true
- `sort_order` - Default: 0

### Field Constraints
- `full_name`: Max 200 characters
- `title`: Max 200 characters
- `content`: No length limit
- `sort_order`: Must be non-negative integer

---

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "full_name": ["This field may not be blank."],
    "content": ["This field is required."]
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

1. Navigate to **"testimonials"** tag
2. Find endpoints
3. Click **"Try it out"** on any endpoint
4. Fill in parameters/body
5. Click **"Execute"**
6. View response

---

## Database Table

**Table Name:** `cms_testimonial`

**Schema:**
```sql
CREATE TABLE cms_testimonial (
    id UUID PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    title VARCHAR(200) NOT NULL,
    image VARCHAR(255),  -- Cloudinary URL
    content TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_testimonial_active ON cms_testimonial(is_active);
CREATE INDEX idx_testimonial_sort ON cms_testimonial(sort_order);
```

---

## Summary

✅ **CMS app created** in `cms/` folder  
✅ **Testimonial model** with all required fields  
✅ **Full CRUD API** with ViewSet  
✅ **Image upload** to Cloudinary  
✅ **Public read access** (active testimonials only)  
✅ **Admin write access** (create/update/delete)  
✅ **Django admin panel** integration  
✅ **Swagger documentation** included  
✅ **Migrations** created and applied  

**The Testimonials API is ready to use!** 🚀

---

## Next Steps

1. **Deploy to production** - Push changes and run migrations
2. **Add seed data** - Create sample testimonials
3. **Frontend integration** - Build testimonials section
4. **Admin UI** - Create management interface
5. **Analytics** - Track testimonial views/engagement
