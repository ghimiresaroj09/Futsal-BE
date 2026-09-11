# Gallery Images API Documentation

## Overview

REST API for managing gallery images with Cloudinary upload, category organization, and full CRUD operations.

**Base URL:** `/api/v1/cms/gallery/images/`

**Date Created:** September 11, 2026

---

## Features

✅ **Full CRUD operations** (Create, Read, Update, Delete)  
✅ **Cloudinary image upload** (automatic storage)  
✅ **Category organization** (foreign key to GalleryCategory)  
✅ **Alt text for accessibility**  
✅ **Sort order within categories**  
✅ **Active/inactive toggle**  
✅ **Public read / Admin write** access  
✅ **Filter by category** and active status  
✅ **Search** by title and alt text  

---

## Database Model

```python
class GalleryImage:
    id: UUID (primary key)
    title: CharField(max_length=200)
    image: ImageField (Cloudinary upload to gallery/)
    alt_text: CharField(max_length=200)
    category: ForeignKey(GalleryCategory, CASCADE)
    is_active: BooleanField (default=True)
    sort_order: IntegerField (default=0)
    created_at: DateTime (auto)
    updated_at: DateTime (auto)
```

---

## API Endpoints

### 🔵 GET - List All Images

**Endpoint:**
```
GET /api/v1/cms/gallery/images/
```

**Authentication:** None (Public)

**Query Parameters:**
- `category` - Filter by category ID
- `is_active` - Filter by active status (true/false)
- `search` - Search in title and alt_text
- `ordering` - Sort by: sort_order, title, created_at, category

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "count": 12,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "uuid",
        "title": "Championship Final 2026",
        "image_url": "https://res.cloudinary.com/.../image.jpg",
        "alt_text": "Team celebrating championship win",
        "category": "category-uuid",
        "category_name": "Tournaments",
        "category_slug": "tournaments",
        "is_active": true,
        "sort_order": 0,
        "created_at": "2026-09-11T19:00:00Z",
        "updated_at": "2026-09-11T19:00:00Z"
      }
    ]
  }
}
```

**Examples:**
```bash
# Get all images
curl "http://localhost:8000/api/v1/cms/gallery/images/"

# Filter by category
curl "http://localhost:8000/api/v1/cms/gallery/images/?category={category-id}"

# Search images
curl "http://localhost:8000/api/v1/cms/gallery/images/?search=tournament"

# Get active images only
curl "http://localhost:8000/api/v1/cms/gallery/images/?is_active=true"
```

---

### 🟢 POST - Upload Image

**Endpoint:**
```
POST /api/v1/cms/gallery/images/
```

**Authentication:** Required (Admin only)

**Content-Type:** `multipart/form-data`

**Request Body:**
```
title: "Championship Final 2026"
image: [file upload]
alt_text: "Team celebrating championship win"
category: "category-uuid"
is_active: true
sort_order: 0
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Gallery image uploaded successfully.",
  "data": {
    "id": "new-uuid",
    "title": "Championship Final 2026",
    "image_url": "https://res.cloudinary.com/.../image.jpg",
    "alt_text": "Team celebrating championship win",
    "category": "category-uuid",
    "category_name": "Tournaments",
    "category_slug": "tournaments",
    "is_active": true,
    "sort_order": 0,
    "created_at": "2026-09-11T19:05:00Z",
    "updated_at": "2026-09-11T19:05:00Z"
  }
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/cms/gallery/images/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "title=Championship Final 2026" \
  -F "image=@/path/to/image.jpg" \
  -F "alt_text=Team celebrating championship win" \
  -F "category=category-uuid" \
  -F "is_active=true" \
  -F "sort_order=0"
```

---

### 🟡 PATCH - Update Image

**Endpoint:**
```
PATCH /api/v1/cms/gallery/images/{id}/
```

**Authentication:** Required (Admin only)

**Content-Type:** `multipart/form-data` or `application/json`

**Request Body (all fields optional):**
```
title: "Updated Title"
image: [file upload] (optional)
alt_text: "Updated alt text"
category: "new-category-uuid"
is_active: false
sort_order: 5
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Gallery image updated successfully.",
  "data": {
    "id": "uuid",
    "title": "Updated Title",
    "image_url": "https://res.cloudinary.com/.../updated.jpg",
    "alt_text": "Updated alt text",
    "category": "new-category-uuid",
    "category_name": "Events",
    "category_slug": "events",
    "is_active": false,
    "sort_order": 5,
    "created_at": "2026-09-11T19:00:00Z",
    "updated_at": "2026-09-11T19:10:00Z"
  }
}
```

---

### 🔴 DELETE - Delete Image

**Endpoint:**
```
DELETE /api/v1/cms/gallery/images/{id}/
```

**Authentication:** Required (Admin only)

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Gallery image deleted successfully.",
  "data": {
    "id": "uuid",
    "title": "Deleted Image"
  }
}
```

---

## Frontend Integration

### React Example - Gallery Grid

```jsx
import { useEffect, useState } from 'react';

function GalleryGrid({ categorySlug }) {
  const [images, setImages] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadData();
  }, []);
  
  const loadData = async () => {
    const [categoriesRes, imagesRes] = await Promise.all([
      fetch('/api/v1/cms/gallery/category/'),
      fetch('/api/v1/cms/gallery/images/')
    ]);
    
    const categoriesData = await categoriesRes.json();
    const imagesData = await imagesRes.json();
    
    setCategories(categoriesData.data.results);
    setImages(imagesData.data.results);
    setLoading(false);
  };
  
  const filterByCategory = (categoryId) => {
    setSelectedCategory(categoryId);
  };
  
  const filteredImages = selectedCategory
    ? images.filter(img => img.category === selectedCategory)
    : images;
  
  if (loading) return <div>Loading gallery...</div>;
  
  return (
    <div className="gallery-container">
      {/* Category Tabs */}
      <div className="category-tabs">
        <button 
          onClick={() => setSelectedCategory(null)}
          className={!selectedCategory ? 'active' : ''}
        >
          All
        </button>
        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => filterByCategory(cat.id)}
            className={selectedCategory === cat.id ? 'active' : ''}
          >
            {cat.name}
          </button>
        ))}
      </div>
      
      {/* Image Grid */}
      <div className="image-grid">
        {filteredImages.map(image => (
          <div key={image.id} className="image-card">
            <img 
              src={image.image_url} 
              alt={image.alt_text}
              loading="lazy"
            />
            <div className="image-overlay">
              <h3>{image.title}</h3>
              <span className="category-badge">
                {image.category_name}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default GalleryGrid;
```

---

### React Example - Admin Upload Form

```jsx
import { useState, useEffect } from 'react';

function GalleryImageUpload() {
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    title: '',
    image: null,
    alt_text: '',
    category: '',
    is_active: true,
    sort_order: 0
  });
  const [loading, setLoading] = useState(false);
  const adminToken = localStorage.getItem('adminToken');
  
  useEffect(() => {
    loadCategories();
  }, []);
  
  const loadCategories = async () => {
    const response = await fetch('/api/v1/cms/gallery/category/');
    const result = await response.json();
    setCategories(result.data.results);
  };
  
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    setFormData({...formData, image: file});
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const formDataToSend = new FormData();
    formDataToSend.append('title', formData.title);
    formDataToSend.append('image', formData.image);
    formDataToSend.append('alt_text', formData.alt_text);
    formDataToSend.append('category', formData.category);
    formDataToSend.append('is_active', formData.is_active);
    formDataToSend.append('sort_order', formData.sort_order);
    
    try {
      const response = await fetch('/api/v1/cms/gallery/images/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${adminToken}`
        },
        body: formDataToSend
      });
      
      const result = await response.json();
      
      if (result.status === 'success') {
        alert('Image uploaded successfully!');
        setFormData({
          title: '',
          image: null,
          alt_text: '',
          category: '',
          is_active: true,
          sort_order: 0
        });
      } else {
        alert('Error: ' + JSON.stringify(result.errors));
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to upload image');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="upload-form">
      <h2>Upload Gallery Image</h2>
      
      <input
        type="text"
        placeholder="Image title"
        value={formData.title}
        onChange={(e) => setFormData({...formData, title: e.target.value})}
        required
        maxLength={200}
      />
      
      <input
        type="file"
        accept="image/*"
        onChange={handleImageChange}
        required
      />
      
      <input
        type="text"
        placeholder="Alt text (for accessibility)"
        value={formData.alt_text}
        onChange={(e) => setFormData({...formData, alt_text: e.target.value})}
        required
        maxLength={200}
      />
      
      <select
        value={formData.category}
        onChange={(e) => setFormData({...formData, category: e.target.value})}
        required
      >
        <option value="">Select category</option>
        {categories.map(cat => (
          <option key={cat.id} value={cat.id}>
            {cat.name}
          </option>
        ))}
      </select>
      
      <label>
        <input
          type="checkbox"
          checked={formData.is_active}
          onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
        />
        Active
      </label>
      
      <input
        type="number"
        placeholder="Sort order"
        value={formData.sort_order}
        onChange={(e) => setFormData({...formData, sort_order: parseInt(e.target.value)})}
        min={0}
      />
      
      <button type="submit" disabled={loading}>
        {loading ? 'Uploading...' : 'Upload Image'}
      </button>
    </form>
  );
}

export default GalleryImageUpload;
```

---

## Validation Rules

### Title
- Required
- Max length: 200 characters
- Cannot be empty or whitespace only

### Image
- Required on create
- Optional on update (keeps existing if not provided)
- Uploaded to Cloudinary `gallery/` folder
- Max size: 5MB (configurable)

### Alt Text
- Required
- Max length: 200 characters
- Cannot be empty or whitespace only
- Important for accessibility

### Category
- Required
- Must be a valid GalleryCategory ID
- Category must be active
- Foreign key with CASCADE delete

### Sort Order
- Optional, defaults to 0
- Must be >= 0 (non-negative)
- Controls order within category

### Is Active
- Optional, defaults to true
- Boolean (true/false)
- Controls public visibility

---

## Error Responses

### 400 Bad Request (Validation)
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "title": ["Title cannot be empty."],
    "alt_text": ["Alt text cannot be empty."],
    "category": ["Cannot add images to an inactive category."]
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

Access: `http://localhost:8000/api/v1/docs/`

1. Navigate to **"cms"** tag
2. Find `/api/v1/cms/gallery/images/` endpoints
3. **GET** - Try without auth
4. **POST/PATCH/DELETE** - Authorize with admin token

---

## CSS Example

```css
.gallery-container {
  padding: 60px 20px;
}

.category-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.category-tabs button {
  padding: 10px 20px;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.category-tabs button.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.image-card {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 4/3;
  cursor: pointer;
}

.image-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.image-card:hover img {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  color: white;
  transform: translateY(100%);
  transition: transform 0.3s;
}

.image-card:hover .image-overlay {
  transform: translateY(0);
}

.category-badge {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(255,255,255,0.2);
  border-radius: 12px;
  font-size: 0.875rem;
  margin-top: 8px;
}
```

---

## Summary

✅ **GalleryImage model** created with category FK  
✅ **Full CRUD API** endpoints  
✅ **Cloudinary integration** for image storage  
✅ **Category organization** (filter/search)  
✅ **Public read access** (active images from active categories)  
✅ **Admin write access** (full control)  
✅ **Accessibility** (required alt text)  
✅ **Django admin panel** integration  
✅ **Swagger documentation**  
✅ **Migration** created and applied  

**The Gallery Images API is ready to use!** 🚀

**Test it at:** `http://localhost:8000/api/v1/docs/` → Look for "cms" tag → "gallery/images"

---

**Last Updated:** September 11, 2026  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
