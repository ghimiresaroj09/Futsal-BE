# Gallery Category API Documentation

## Overview

REST API for managing gallery categories to organize images and videos. Full CRUD operations (Create, Read, Update, Delete) are available for administrators.

**Base URL:** `/api/v1/cms/gallery/category/`

**Date Created:** September 11, 2026

---

## Features

✅ **Full CRUD operations** (Create, Read, Update, Delete)  
✅ **Auto-generated slug** from name (URL-friendly)  
✅ **Unique category names** (case-insensitive validation)  
✅ **Sort order control** (display sequence)  
✅ **Active/inactive toggle** (visibility control)  
✅ **Public read access** (view categories)  
✅ **Admin-only write access** (create/update/delete)  
✅ **Search & filter** capabilities  
✅ **Swagger documentation**  

---

## Database Model

```python
class GalleryCategory:
    id: UUID (primary key)
    name: CharField(max_length=100, unique=True)
    slug: SlugField(max_length=100, unique=True, auto-generated)
    description: TextField (optional)
    is_active: BooleanField (default=True)
    sort_order: IntegerField (default=0)
    created_at: DateTime (auto)
    updated_at: DateTime (auto)
```

---

## API Endpoints

### 🔵 GET - List All Categories

**Endpoint:**
```
GET /api/v1/cms/gallery/category/
```

**Authentication:** None (Public)

**Query Parameters:**
- `is_active` - Filter by active status (true/false)
- `search` - Search in name and description
- `ordering` - Sort by: sort_order, name, created_at

**Description:** Returns all active gallery categories. Admins see all categories including inactive ones.

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/cms/gallery/category/"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "uuid-here",
        "name": "Tournaments",
        "slug": "tournaments",
        "description": "Tournament photos and videos",
        "is_active": true,
        "sort_order": 0,
        "created_at": "2026-09-11T19:00:00Z",
        "updated_at": "2026-09-11T19:00:00Z"
      },
      {
        "id": "uuid-here",
        "name": "Facilities",
        "slug": "facilities",
        "description": "Venue and facilities showcase",
        "is_active": true,
        "sort_order": 1,
        "created_at": "2026-09-11T19:00:00Z",
        "updated_at": "2026-09-11T19:00:00Z"
      },
      {
        "id": "uuid-here",
        "name": "Events",
        "slug": "events",
        "description": "Special events and celebrations",
        "is_active": true,
        "sort_order": 2,
        "created_at": "2026-09-11T19:00:00Z",
        "updated_at": "2026-09-11T19:00:00Z"
      }
    ]
  }
}
```

**With Filters:**
```bash
# Get only active categories
curl "http://localhost:8000/api/v1/cms/gallery/category/?is_active=true"

# Search categories
curl "http://localhost:8000/api/v1/cms/gallery/category/?search=tournament"

# Sort by name
curl "http://localhost:8000/api/v1/cms/gallery/category/?ordering=name"
```

---

### 🔵 GET - Get Single Category

**Endpoint:**
```
GET /api/v1/cms/gallery/category/{id}/
```

**Authentication:** None (Public)

**Description:** Returns details of a specific gallery category.

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/cms/gallery/category/{category-id}/"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Success",
  "data": {
    "id": "uuid-here",
    "name": "Tournaments",
    "slug": "tournaments",
    "description": "Tournament photos and videos",
    "is_active": true,
    "sort_order": 0,
    "created_at": "2026-09-11T19:00:00Z",
    "updated_at": "2026-09-11T19:00:00Z"
  }
}
```

---

### 🟢 POST - Create Category

**Endpoint:**
```
POST /api/v1/cms/gallery/category/
```

**Authentication:** Required (Admin only)

**Content-Type:** `application/json`

**Description:** Create a new gallery category. The slug is auto-generated from the name.

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Request Body:**
```json
{
  "name": "Team Photos",
  "description": "Team and player photographs",
  "is_active": true,
  "sort_order": 3
}
```

**Field Reference:**
```json
{
  "name": "string (required, max 100 chars, unique)",
  "description": "string (optional)",
  "is_active": "boolean (optional, default: true)",
  "sort_order": "integer (optional, default: 0, min: 0)"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "Gallery category created successfully.",
  "data": {
    "id": "new-uuid",
    "name": "Team Photos",
    "slug": "team-photos",
    "description": "Team and player photographs",
    "is_active": true,
    "sort_order": 3,
    "created_at": "2026-09-11T19:05:00Z",
    "updated_at": "2026-09-11T19:05:00Z"
  }
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/cms/gallery/category/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "name": "Team Photos",
    "description": "Team and player photographs",
    "is_active": true,
    "sort_order": 3
  }'
```

---

### 🟡 PATCH - Update Category

**Endpoint:**
```
PATCH /api/v1/cms/gallery/category/{id}/
```

**Authentication:** Required (Admin only)

**Content-Type:** `application/json`

**Description:** Update gallery category details. Only include fields you want to change.

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Request Body (all fields optional):**
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "is_active": false,
  "sort_order": 5
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Gallery category updated successfully.",
  "data": {
    "id": "uuid-here",
    "name": "Updated Name",
    "slug": "updated-name",
    "description": "Updated description",
    "is_active": false,
    "sort_order": 5,
    "created_at": "2026-09-11T19:00:00Z",
    "updated_at": "2026-09-11T19:10:00Z"
  }
}
```

**cURL Example:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/gallery/category/{category-id}/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "description": "Updated description text"
  }'
```

---

### 🔴 DELETE - Delete Category

**Endpoint:**
```
DELETE /api/v1/cms/gallery/category/{id}/
```

**Authentication:** Required (Admin only)

**Description:** Delete a gallery category permanently.

**Request Headers:**
```
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Gallery category deleted successfully.",
  "data": {
    "id": "uuid-here",
    "name": "Deleted Category"
  }
}
```

**cURL Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/cms/gallery/category/{category-id}/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Frontend Integration

### React Example - List Categories

```jsx
import { useEffect, useState } from 'react';

function GalleryCategoriesList() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadCategories();
  }, []);
  
  const loadCategories = async () => {
    try {
      const response = await fetch('/api/v1/cms/gallery/category/');
      const result = await response.json();
      setCategories(result.data.results);
    } catch (error) {
      console.error('Failed to load categories:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <div>Loading categories...</div>;
  
  return (
    <div className="gallery-categories">
      <h2>Gallery Categories</h2>
      <ul>
        {categories.map(category => (
          <li key={category.id}>
            <a href={`/gallery/${category.slug}`}>
              {category.name}
            </a>
            {category.description && (
              <p>{category.description}</p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default GalleryCategoriesList;
```

---

### React Example - Admin CRUD

```jsx
import { useState, useEffect } from 'react';

function CategoryManager() {
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    is_active: true,
    sort_order: 0
  });
  const [editingId, setEditingId] = useState(null);
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
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const url = editingId
      ? `/api/v1/cms/gallery/category/${editingId}/`
      : '/api/v1/cms/gallery/category/';
    
    const method = editingId ? 'PATCH' : 'POST';
    
    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${adminToken}`
        },
        body: JSON.stringify(formData)
      });
      
      const result = await response.json();
      
      if (result.status === 'success') {
        alert(editingId ? 'Category updated!' : 'Category created!');
        setFormData({ name: '', description: '', is_active: true, sort_order: 0 });
        setEditingId(null);
        loadCategories();
      } else {
        alert('Error: ' + JSON.stringify(result.errors));
      }
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred');
    } finally {
      setLoading(false);
    }
  };
  
  const handleEdit = (category) => {
    setFormData({
      name: category.name,
      description: category.description,
      is_active: category.is_active,
      sort_order: category.sort_order
    });
    setEditingId(category.id);
  };
  
  const handleDelete = async (id, name) => {
    if (!confirm(`Delete category "${name}"?`)) return;
    
    try {
      const response = await fetch(`/api/v1/cms/gallery/category/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${adminToken}`
        }
      });
      
      const result = await response.json();
      
      if (result.status === 'success') {
        alert('Category deleted!');
        loadCategories();
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to delete category');
    }
  };
  
  return (
    <div className="category-manager">
      <h2>Gallery Category Manager</h2>
      
      <form onSubmit={handleSubmit} className="category-form">
        <h3>{editingId ? 'Edit Category' : 'Create Category'}</h3>
        
        <input
          type="text"
          placeholder="Category name"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          required
          maxLength={100}
        />
        
        <textarea
          placeholder="Description (optional)"
          value={formData.description}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
          rows={3}
        />
        
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
        
        <div className="button-group">
          <button type="submit" disabled={loading}>
            {loading ? 'Saving...' : (editingId ? 'Update' : 'Create')}
          </button>
          
          {editingId && (
            <button 
              type="button" 
              onClick={() => {
                setEditingId(null);
                setFormData({ name: '', description: '', is_active: true, sort_order: 0 });
              }}
            >
              Cancel
            </button>
          )}
        </div>
      </form>
      
      <div className="categories-list">
        <h3>Existing Categories</h3>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Slug</th>
              <th>Status</th>
              <th>Sort Order</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {categories.map(category => (
              <tr key={category.id}>
                <td>{category.name}</td>
                <td>{category.slug}</td>
                <td>{category.is_active ? 'Active' : 'Inactive'}</td>
                <td>{category.sort_order}</td>
                <td>
                  <button onClick={() => handleEdit(category)}>Edit</button>
                  <button onClick={() => handleDelete(category.id, category.name)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default CategoryManager;
```

---

### Vue.js Example

```vue
<template>
  <div class="gallery-categories">
    <h2>Gallery</h2>
    <ul class="category-tabs">
      <li 
        v-for="category in categories" 
        :key="category.id"
        :class="{ active: selectedCategory === category.slug }"
        @click="selectCategory(category.slug)"
      >
        {{ category.name }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      categories: [],
      selectedCategory: null
    };
  },
  
  mounted() {
    this.loadCategories();
  },
  
  methods: {
    async loadCategories() {
      try {
        const response = await fetch('/api/v1/cms/gallery/category/');
        const result = await response.json();
        this.categories = result.data.results;
        
        if (this.categories.length > 0) {
          this.selectedCategory = this.categories[0].slug;
        }
      } catch (error) {
        console.error('Failed to load categories:', error);
      }
    },
    
    selectCategory(slug) {
      this.selectedCategory = slug;
      this.$emit('category-selected', slug);
    }
  }
};
</script>
```

---

## Validation Rules

### Name
- **Required**
- Max length: 100 characters
- Must be unique (case-insensitive)
- Cannot be empty or whitespace only
- Auto-generates slug on save

### Description
- Optional
- Can be any text length
- Defaults to empty string

### Slug
- Auto-generated from name
- URL-friendly (lowercase, hyphens)
- Unique
- Read-only (cannot be manually set)

### Sort Order
- Optional, defaults to 0
- Must be >= 0 (non-negative)
- Used for display ordering

### Is Active
- Optional, defaults to true
- Boolean (true/false)
- Controls visibility for public

---

## Error Responses

### 400 Bad Request (Validation Error)
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "name": ["Category name cannot be empty."]
  }
}
```

### 400 Bad Request (Duplicate Name)
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "name": ["A category with name 'Tournaments' already exists."]
  }
}
```

### 400 Bad Request (Negative Sort Order)
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "sort_order": ["Sort order cannot be negative."]
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
2. Find `/api/v1/cms/gallery/category/` endpoints
3. **GET** - Click "Try it out" → "Execute" (no auth needed)
4. **POST/PATCH/DELETE** - Click "Authorize" → Add admin token → Test operations

---

## Common Use Cases

### 1. Create Default Categories
```javascript
const createDefaultCategories = async () => {
  const categories = [
    { name: 'Tournaments', description: 'Tournament photos and videos', sort_order: 0 },
    { name: 'Facilities', description: 'Venue and facilities showcase', sort_order: 1 },
    { name: 'Events', description: 'Special events and celebrations', sort_order: 2 },
    { name: 'Team Photos', description: 'Team and player photographs', sort_order: 3 }
  ];
  
  for (const cat of categories) {
    await fetch('/api/v1/cms/gallery/category/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${adminToken}`
      },
      body: JSON.stringify(cat)
    });
  }
};
```

### 2. Get Categories for Navigation
```javascript
const getNavCategories = async () => {
  const response = await fetch('/api/v1/cms/gallery/category/?ordering=sort_order');
  const result = await response.json();
  return result.data.results;
};
```

### 3. Toggle Category Active Status
```javascript
const toggleActive = async (categoryId, currentStatus) => {
  await fetch(`/api/v1/cms/gallery/category/${categoryId}/`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${adminToken}`
    },
    body: JSON.stringify({
      is_active: !currentStatus
    })
  });
};
```

### 4. Reorder Categories
```javascript
const reorderCategories = async (categoryUpdates) => {
  // categoryUpdates: [{id, sort_order}, ...]
  await Promise.all(
    categoryUpdates.map(update =>
      fetch(`/api/v1/cms/gallery/category/${update.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${adminToken}`
        },
        body: JSON.stringify({
          sort_order: update.sort_order
        })
      })
    )
  );
};
```

---

## Summary

✅ **GalleryCategory model** created  
✅ **Full CRUD API** endpoints  
✅ **Auto-generated slugs** from name  
✅ **Unique name validation** (case-insensitive)  
✅ **Public read access** (active categories)  
✅ **Admin write access** (full control)  
✅ **Search & filter** support  
✅ **Django admin panel** integration  
✅ **Swagger documentation**  
✅ **Migration** created and applied  

**The Gallery Category API is ready to use!** 🚀

**Test it at:** `http://localhost:8000/api/v1/docs/` → Look for "cms" tag → "gallery/category"

---

**Last Updated:** September 11, 2026  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
