# Arena Section API Documentation

## Overview

REST API for managing the homepage arena section with title, description, and a features array. This is a singleton endpoint - only one arena section exists.

**Base URL:** `/api/v1/cms/homepage/arena/`

**Date Created:** September 11, 2026

---

## Features

✅ **Singleton pattern** (only one arena section)  
✅ **JSON-based features array** (flexible list of strings)  
✅ **Public read access** (anyone can view)  
✅ **Admin-only write access** (update requires authentication)  
✅ **Automatic timestamps**  
✅ **Swagger documentation**  
✅ **Array validation** (ensures features is a list of non-empty strings)  

---

## Database Model

```python
class ArenaSection:
    title: CharField(max_length=200)
    description: TextField
    features: JSONField (array of strings)
    updated_at: DateTime (auto)
```

---

## API Endpoints

### 🔵 GET - Retrieve Arena Section

**Endpoint:**
```
GET /api/v1/cms/homepage/arena/
```

**Authentication:** None (Public)

**Description:** Returns the homepage arena section content including title, description, and features array.

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/cms/homepage/arena/"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Arena section retrieved successfully.",
  "data": {
    "title": "Our Premium Arena",
    "description": "Experience world-class futsal facilities with state-of-the-art equipment and professional-grade playing surfaces. Our arena is designed to provide the ultimate futsal experience for players of all skill levels.",
    "features": [
      "Professional-grade artificial turf",
      "LED floodlighting system",
      "Climate-controlled indoor facility",
      "Spectator seating for 200+ people",
      "Modern changing rooms and showers",
      "Free parking available",
      "On-site cafe and refreshments",
      "Pro shop with equipment rentals"
    ],
    "updated_at": "2026-09-11T17:12:00Z"
  }
}
```

**JavaScript Example:**
```javascript
const response = await fetch('/api/v1/cms/homepage/arena/');
const result = await response.json();

console.log(result.data.title);        // "Our Premium Arena"
console.log(result.data.features);     // Array of feature strings
```

---

### 🟡 PATCH - Update Arena Section

**Endpoint:**
```
PATCH /api/v1/cms/homepage/arena/
```

**Authentication:** Required (Admin only)

**Content-Type:** `application/json`

**Description:** Update the arena section content. Only include fields you want to change.

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Request Body (all fields optional):**
```json
{
  "title": "World-Class Futsal Arena",
  "description": "Updated description text here...",
  "features": [
    "International standard court dimensions",
    "Professional lighting system",
    "Premium artificial turf",
    "Spectator gallery",
    "Modern facilities"
  ]
}
```

**Field Reference:**
```json
{
  "title": "string (max 200 chars, optional)",
  "description": "string (optional)",
  "features": ["array of strings (optional)"]
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Arena section updated successfully.",
  "data": {
    "title": "World-Class Futsal Arena",
    "description": "Updated description text here...",
    "features": [
      "International standard court dimensions",
      "Professional lighting system",
      "Premium artificial turf",
      "Spectator gallery",
      "Modern facilities"
    ],
    "updated_at": "2026-09-11T17:15:30Z"
  }
}
```

**cURL Example (Update all fields):**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/homepage/arena/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "title": "World-Class Futsal Arena",
    "description": "Experience the best futsal facilities in the region.",
    "features": [
      "International standard court",
      "Professional lighting",
      "Premium turf",
      "Modern amenities"
    ]
  }'
```

**cURL Example (Update only features):**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/homepage/arena/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "features": [
      "New feature 1",
      "New feature 2",
      "New feature 3"
    ]
  }'
```

**JavaScript Example:**
```javascript
const updateArena = async (updates) => {
  const response = await fetch('/api/v1/cms/homepage/arena/', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${adminToken}`
    },
    body: JSON.stringify(updates)
  });
  
  const result = await response.json();
  return result.data;
};

// Update only the title
await updateArena({
  title: "New Arena Title"
});

// Update only features
await updateArena({
  features: [
    "Feature A",
    "Feature B",
    "Feature C"
  ]
});

// Update multiple fields
await updateArena({
  title: "Premium Arena",
  description: "Best in class facilities",
  features: ["Feature 1", "Feature 2"]
});
```

---

## Frontend Integration

### React Example - Display Arena Section

```jsx
import { useEffect, useState } from 'react';
import { CheckCircle } from 'lucide-react';

function ArenaSection() {
  const [arena, setArena] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadArenaSection();
  }, []);
  
  const loadArenaSection = async () => {
    try {
      const response = await fetch('/api/v1/cms/homepage/arena/');
      const result = await response.json();
      setArena(result.data);
    } catch (error) {
      console.error('Failed to load arena section:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <div>Loading arena details...</div>;
  if (!arena) return null;
  
  return (
    <section className="arena-section">
      <div className="container">
        <h2 className="section-title">{arena.title}</h2>
        <p className="section-description">{arena.description}</p>
        
        <div className="features-grid">
          {arena.features.map((feature, index) => (
            <div key={index} className="feature-item">
              <CheckCircle className="feature-icon" />
              <span>{feature}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default ArenaSection;
```

---

### React Example - Admin Edit Form

```jsx
import { useState, useEffect } from 'react';
import { Plus, X } from 'lucide-react';

function ArenaEditForm() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [features, setFeatures] = useState([]);
  const [newFeature, setNewFeature] = useState('');
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    loadArena();
  }, []);
  
  const loadArena = async () => {
    const response = await fetch('/api/v1/cms/homepage/arena/');
    const result = await response.json();
    
    setTitle(result.data.title);
    setDescription(result.data.description);
    setFeatures(result.data.features);
  };
  
  const addFeature = () => {
    if (newFeature.trim()) {
      setFeatures([...features, newFeature.trim()]);
      setNewFeature('');
    }
  };
  
  const removeFeature = (index) => {
    setFeatures(features.filter((_, i) => i !== index));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch('/api/v1/cms/homepage/arena/', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: JSON.stringify({
          title,
          description,
          features
        })
      });
      
      const result = await response.json();
      
      if (result.status === 'success') {
        alert('Arena section updated successfully!');
      } else {
        alert('Failed to update arena section');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="arena-edit-form">
      <h3>Edit Arena Section</h3>
      
      <div className="form-group">
        <label>Title *</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={200}
          required
        />
      </div>
      
      <div className="form-group">
        <label>Description *</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={5}
          required
        />
      </div>
      
      <div className="form-group">
        <label>Features</label>
        
        <div className="features-list">
          {features.map((feature, index) => (
            <div key={index} className="feature-item">
              <span>{feature}</span>
              <button
                type="button"
                onClick={() => removeFeature(index)}
                className="btn-remove"
              >
                <X size={16} />
              </button>
            </div>
          ))}
        </div>
        
        <div className="add-feature">
          <input
            type="text"
            value={newFeature}
            onChange={(e) => setNewFeature(e.target.value)}
            placeholder="Add a new feature"
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addFeature())}
          />
          <button
            type="button"
            onClick={addFeature}
            className="btn-add"
          >
            <Plus size={16} /> Add
          </button>
        </div>
      </div>
      
      <button type="submit" disabled={loading} className="btn btn-primary">
        {loading ? 'Saving...' : 'Save Changes'}
      </button>
    </form>
  );
}

export default ArenaEditForm;
```

---

### Vue.js Example - Display Arena

```vue
<template>
  <section v-if="arena" class="arena-section">
    <div class="container">
      <h2>{{ arena.title }}</h2>
      <p>{{ arena.description }}</p>
      
      <ul class="features-list">
        <li v-for="(feature, index) in arena.features" :key="index">
          <i class="icon-check"></i>
          {{ feature }}
        </li>
      </ul>
    </div>
  </section>
</template>

<script>
export default {
  data() {
    return {
      arena: null
    };
  },
  
  mounted() {
    this.loadArena();
  },
  
  methods: {
    async loadArena() {
      try {
        const response = await fetch('/api/v1/cms/homepage/arena/');
        const result = await response.json();
        this.arena = result.data;
      } catch (error) {
        console.error('Failed to load arena:', error);
      }
    }
  }
};
</script>
```

---

## Validation Rules

### Field Validation

**Title:**
- Optional on update
- Cannot be empty string if provided
- Max length: 200 characters

**Description:**
- Optional on update
- Can be any text length

**Features:**
- Optional on update
- Must be an array if provided
- Each item must be a string
- Cannot contain empty strings
- Example valid: `["Feature 1", "Feature 2"]`
- Example invalid: `["Feature 1", "", "Feature 2"]` ❌

---

## Error Responses

### 400 Bad Request (Validation Error)
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "title": ["Title cannot be empty."],
    "features": ["Each feature must be a string."]
  }
}
```

### 400 Bad Request (Invalid Features)
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "features": ["Features must be an array."]
  }
}
```

### 400 Bad Request (Empty Feature String)
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "features": ["Features cannot contain empty strings."]
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

---

## Testing with Swagger

Access Swagger UI at: `http://localhost:8000/api/v1/docs/`

1. Navigate to **"cms"** tag
2. Find `/api/v1/cms/homepage/arena/` endpoints
3. **GET** - Click "Try it out" → "Execute" (no auth needed)
4. **PATCH** - Click "Authorize" → Add admin token → "Try it out" → Edit request body → "Execute"

---

## CSS Example for Arena Section

```css
.arena-section {
  padding: 80px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.arena-section .container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-title {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 20px;
  text-align: center;
}

.section-description {
  font-size: 1.2rem;
  line-height: 1.8;
  text-align: center;
  max-width: 800px;
  margin: 0 auto 60px;
  opacity: 0.95;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 40px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  backdrop-filter: blur(10px);
  transition: transform 0.3s, background 0.3s;
}

.feature-item:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
}

.feature-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  color: #4ade80;
}

.feature-item span {
  font-size: 1rem;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .section-title {
    font-size: 2rem;
  }
  
  .section-description {
    font-size: 1rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
}
```

---

## Common Use Cases

### 1. Initial Setup (Admin)
```javascript
// Set up arena section for the first time
const setupArena = async () => {
  await fetch('/api/v1/cms/homepage/arena/', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${adminToken}`
    },
    body: JSON.stringify({
      title: "Premium Futsal Arena",
      description: "State-of-the-art facilities for the ultimate futsal experience",
      features: [
        "Professional-grade turf",
        "LED lighting system",
        "Climate controlled",
        "Spectator seating",
        "Modern facilities"
      ]
    })
  });
};
```

### 2. Add New Feature
```javascript
// Load current data, add feature, update
const addFeature = async (newFeature) => {
  const response = await fetch('/api/v1/cms/homepage/arena/');
  const result = await response.json();
  
  const updatedFeatures = [...result.data.features, newFeature];
  
  await fetch('/api/v1/cms/homepage/arena/', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${adminToken}`
    },
    body: JSON.stringify({ features: updatedFeatures })
  });
};
```

### 3. Remove Feature
```javascript
// Load, filter, update
const removeFeature = async (featureToRemove) => {
  const response = await fetch('/api/v1/cms/homepage/arena/');
  const result = await response.json();
  
  const updatedFeatures = result.data.features.filter(
    f => f !== featureToRemove
  );
  
  await fetch('/api/v1/cms/homepage/arena/', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${adminToken}`
    },
    body: JSON.stringify({ features: updatedFeatures })
  });
};
```

---

## Summary

✅ **ArenaSection model** created (singleton)  
✅ **GET/PATCH API** endpoints  
✅ **JSONField for features array**  
✅ **Public read access**  
✅ **Admin write access**  
✅ **Array validation** (non-empty strings)  
✅ **Django admin panel** integration  
✅ **Swagger documentation**  
✅ **Migration** created and applied  

**The Arena Section API is ready to use!** 🚀

**Test it at:** `http://localhost:8000/api/v1/docs/` → Look for "cms" tag → "homepage/arena"

---

**Last Updated:** September 11, 2026  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
