# Hero Section API Documentation

## Overview

API for managing the homepage hero section content (singleton). Only one hero section exists and can be updated via PATCH.

**Endpoint:** `/api/v1/cms/homepage/hero-section/`

**Date Created:** September 11, 2026

---

## Features

✅ **Singleton pattern** (only one hero section exists)  
✅ **GET endpoint** (public access)  
✅ **PATCH endpoint** (admin-only update)  
✅ **Image upload** to Cloudinary  
✅ **Structured stats** (3 stat items)  
✅ **Partial updates** (only send changed fields)  
✅ **Automatic timestamps**  
✅ **Swagger documentation**  

---

## Database Model

```python
class HeroSection(SingletonModel):
    title_one: CharField(max_length=200)
    title_two: CharField(max_length=200)
    description: TextField
    image: ImageField (optional, stored in Cloudinary)
    
    # Stat 1 - Open
    stat_open_label: CharField(max_length=100, default="Open every day")
    stat_open_value: CharField(max_length=50, default="7 Days/Week")
    
    # Stat 2 - Matches
    stat_matches_label: CharField(max_length=100, default="Matches hosted")
    stat_matches_value: CharField(max_length=50, default="500+")
    
    # Stat 3 - Courts
    stat_courts_label: CharField(max_length=100, default="Premium courts")
    stat_courts_value: CharField(max_length=50, default="2 Courts")
    
    updated_at: DateTime (auto)
```

---

## API Endpoints

### 🔵 GET - Retrieve Hero Section

**Endpoint:**
```
GET /api/v1/cms/homepage/hero-section/
```

**Authentication:** None (Public)

**Description:** Returns the homepage hero section content including titles, description, image, and stats.

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/cms/homepage/hero-section/"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Hero section retrieved successfully.",
  "data": {
    "title_one": "Play Futsal",
    "title_two": "At Its Best",
    "description": "Experience the thrill of futsal at our premium indoor facility. Book your slot online and join the action today!",
    "image_url": "https://res.cloudinary.com/demo/image/upload/v1/hero/hero-bg.jpg",
    "stats": [
      {
        "label": "Open every day",
        "value": "7 Days/Week"
      },
      {
        "label": "Matches hosted",
        "value": "500+"
      },
      {
        "label": "Premium courts",
        "value": "2 Courts"
      }
    ],
    "updated_at": "2026-09-11T16:45:00Z"
  }
}
```

**Response (No Image):**
```json
{
  "status": "success",
  "message": "Hero section retrieved successfully.",
  "data": {
    "title_one": "Play Futsal",
    "title_two": "At Its Best",
    "description": "Experience the thrill of futsal...",
    "image_url": null,
    "stats": [
      {
        "label": "Open every day",
        "value": "7 Days/Week"
      },
      {
        "label": "Matches hosted",
        "value": "500+"
      },
      {
        "label": "Premium courts",
        "value": "2 Courts"
      }
    ],
    "updated_at": "2026-09-11T16:45:00Z"
  }
}
```

**JavaScript Example:**
```javascript
async function loadHeroSection() {
  try {
    const response = await fetch('/api/v1/cms/homepage/hero-section/');
    const result = await response.json();
    
    const hero = result.data;
    
    // Update hero section
    document.getElementById('hero-title-1').textContent = hero.title_one;
    document.getElementById('hero-title-2').textContent = hero.title_two;
    document.getElementById('hero-description').textContent = hero.description;
    
    if (hero.image_url) {
      document.getElementById('hero-bg').style.backgroundImage = `url(${hero.image_url})`;
    }
    
    // Render stats
    const statsHTML = hero.stats.map(stat => `
      <div class="stat-item">
        <h3>${stat.value}</h3>
        <p>${stat.label}</p>
      </div>
    `).join('');
    document.getElementById('hero-stats').innerHTML = statsHTML;
    
  } catch (error) {
    console.error('Failed to load hero section:', error);
  }
}

// Load on page load
loadHeroSection();
```

---

### 🟡 PATCH - Update Hero Section

**Endpoint:**
```
PATCH /api/v1/cms/homepage/hero-section/
```

**Authentication:** Required (Admin only)

**Content-Type:** `multipart/form-data` or `application/json`

**Description:** Update hero section content. Only include fields you want to change.

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Request Body Example 1 (Update text only - JSON):**
```json
{
  "title_one": "Experience Futsal",
  "title_two": "Like Never Before",
  "description": "Join Nepal's premier futsal arena. Premium courts, professional lighting, and easy online booking."
}
```

**Request Body Example 2 (Update stats - JSON):**
```json
{
  "stat_open_label": "Available",
  "stat_open_value": "24/7",
  "stat_matches_label": "Games played",
  "stat_matches_value": "1000+",
  "stat_courts_label": "Indoor courts",
  "stat_courts_value": "3 Courts"
}
```

**Request Body Example 3 (Replace image - form-data):**
```
image: [Binary file: new-hero-bg.jpg]
```

**Request Body Example 4 (Update everything - form-data):**
```
title_one: "Experience Futsal"
title_two: "Like Never Before"
description: "Join Nepal's premier futsal arena..."
image: [Binary file: hero-background.jpg]
stat_open_label: "Available"
stat_open_value: "24/7"
stat_matches_label: "Games played"
stat_matches_value: "1000+"
stat_courts_label: "Indoor courts"
stat_courts_value: "3 Courts"
```

**Full Field Reference:**
```
title_one (optional): First line of title (max 200 chars)
title_two (optional): Second line of title (max 200 chars)
description (optional): Hero description text
image (optional): Image file (JPEG, PNG, WebP)

stat_open_label (optional): Label for stat 1 (max 100 chars)
stat_open_value (optional): Value for stat 1 (max 50 chars)

stat_matches_label (optional): Label for stat 2 (max 100 chars)
stat_matches_value (optional): Value for stat 2 (max 50 chars)

stat_courts_label (optional): Label for stat 3 (max 100 chars)
stat_courts_value (optional): Value for stat 3 (max 50 chars)
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Hero section updated successfully.",
  "data": {
    "title_one": "Experience Futsal",
    "title_two": "Like Never Before",
    "description": "Join Nepal's premier futsal arena. Premium courts, professional lighting, and easy online booking.",
    "image_url": "https://res.cloudinary.com/demo/image/upload/v1726234900/hero/hero-background.jpg",
    "stats": [
      {
        "label": "Available",
        "value": "24/7"
      },
      {
        "label": "Games played",
        "value": "1000+"
      },
      {
        "label": "Indoor courts",
        "value": "3 Courts"
      }
    ],
    "updated_at": "2026-09-11T16:50:00Z"
  }
}
```

**cURL Example (Update text):**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/homepage/hero-section/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "title_one": "Experience Futsal",
    "title_two": "Like Never Before",
    "description": "Join Nepal'\''s premier futsal arena..."
  }'
```

**cURL Example (Replace image):**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/homepage/hero-section/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "image=@/path/to/hero-background.jpg"
```

**cURL Example (Update stats):**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/homepage/hero-section/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "stat_matches_label": "Games played",
    "stat_matches_value": "1000+"
  }'
```

**JavaScript Example (Update text):**
```javascript
async function updateHeroSection(updates) {
  try {
    const response = await fetch('/api/v1/cms/homepage/hero-section/', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${adminToken}`
      },
      body: JSON.stringify(updates)
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      alert('Hero section updated successfully!');
      loadHeroSection(); // Refresh display
    } else {
      alert('Failed to update hero section');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('An error occurred');
  }
}

// Usage - update titles
updateHeroSection({
  title_one: 'Experience Futsal',
  title_two: 'Like Never Before'
});

// Usage - update a stat
updateHeroSection({
  stat_matches_value: '1000+'
});
```

**JavaScript Example (Replace image):**
```javascript
async function updateHeroImage(file) {
  const formData = new FormData();
  formData.append('image', file);
  
  try {
    const response = await fetch('/api/v1/cms/homepage/hero-section/', {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${adminToken}`
      },
      body: formData
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      alert('Hero image updated successfully!');
      // Update background
      document.getElementById('hero-bg').style.backgroundImage = 
        `url(${result.data.image_url})`;
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Usage
const fileInput = document.getElementById('hero-image-input');
fileInput.addEventListener('change', (e) => {
  updateHeroImage(e.target.files[0]);
});
```

---

## Frontend Integration

### React Example - Hero Section Display

```jsx
import { useEffect, useState } from 'react';

function HeroSection() {
  const [hero, setHero] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadHero();
  }, []);
  
  const loadHero = async () => {
    try {
      const response = await fetch('/api/v1/cms/homepage/hero-section/');
      const result = await response.json();
      setHero(result.data);
    } catch (error) {
      console.error('Failed to load hero section:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <div>Loading...</div>;
  if (!hero) return null;
  
  return (
    <section 
      className="hero-section"
      style={hero.image_url ? {
        backgroundImage: `url(${hero.image_url})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      } : {}}
    >
      <div className="hero-content">
        <h1 className="hero-title">
          <span className="title-line-1">{hero.title_one}</span>
          <span className="title-line-2">{hero.title_two}</span>
        </h1>
        
        <p className="hero-description">{hero.description}</p>
        
        <div className="hero-stats">
          {hero.stats.map((stat, index) => (
            <div key={index} className="stat-item">
              <h3 className="stat-value">{stat.value}</h3>
              <p className="stat-label">{stat.label}</p>
            </div>
          ))}
        </div>
        
        <div className="hero-actions">
          <button className="btn btn-primary">Book Now</button>
          <button className="btn btn-secondary">View Slots</button>
        </div>
      </div>
    </section>
  );
}

export default HeroSection;
```

---

### React Example - Admin Edit Form

```jsx
import { useState, useEffect } from 'react';

function HeroSectionEditor() {
  const [hero, setHero] = useState({
    title_one: '',
    title_two: '',
    description: '',
    stat_open_label: '',
    stat_open_value: '',
    stat_matches_label: '',
    stat_matches_value: '',
    stat_courts_label: '',
    stat_courts_value: ''
  });
  const [imageFile, setImageFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  useEffect(() => {
    loadHero();
  }, []);
  
  const loadHero = async () => {
    try {
      const response = await fetch('/api/v1/cms/homepage/hero-section/');
      const result = await response.json();
      
      // Map stats back to form
      setHero({
        title_one: result.data.title_one,
        title_two: result.data.title_two,
        description: result.data.description,
        stat_open_label: result.data.stats[0].label,
        stat_open_value: result.data.stats[0].value,
        stat_matches_label: result.data.stats[1].label,
        stat_matches_value: result.data.stats[1].value,
        stat_courts_label: result.data.stats[2].label,
        stat_courts_value: result.data.stats[2].value
      });
    } catch (error) {
      console.error('Failed to load hero section:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    
    const formData = new FormData();
    
    // Add text fields
    Object.keys(hero).forEach(key => {
      formData.append(key, hero[key]);
    });
    
    // Add image if selected
    if (imageFile) {
      formData.append('image', imageFile);
    }
    
    try {
      const response = await fetch('/api/v1/cms/homepage/hero-section/', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
        },
        body: formData
      });
      
      const result = await response.json();
      
      if (result.status === 'success') {
        alert('Hero section updated successfully!');
        loadHero(); // Refresh data
        setImageFile(null);
      } else {
        alert('Failed to update hero section');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred');
    } finally {
      setSaving(false);
    }
  };
  
  if (loading) return <div>Loading editor...</div>;
  
  return (
    <form onSubmit={handleSubmit} className="hero-editor">
      <h2>Edit Hero Section</h2>
      
      <div className="form-section">
        <h3>Titles</h3>
        
        <div className="form-group">
          <label>Title Line 1 *</label>
          <input
            type="text"
            value={hero.title_one}
            onChange={(e) => setHero({...hero, title_one: e.target.value})}
            required
            maxLength={200}
          />
        </div>
        
        <div className="form-group">
          <label>Title Line 2 *</label>
          <input
            type="text"
            value={hero.title_two}
            onChange={(e) => setHero({...hero, title_two: e.target.value})}
            required
            maxLength={200}
          />
        </div>
        
        <div className="form-group">
          <label>Description</label>
          <textarea
            value={hero.description}
            onChange={(e) => setHero({...hero, description: e.target.value})}
            rows={4}
          />
        </div>
      </div>
      
      <div className="form-section">
        <h3>Background Image</h3>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setImageFile(e.target.files[0])}
        />
      </div>
      
      <div className="form-section">
        <h3>Stats</h3>
        
        <div className="form-row">
          <div className="form-group">
            <label>Stat 1 Label</label>
            <input
              type="text"
              value={hero.stat_open_label}
              onChange={(e) => setHero({...hero, stat_open_label: e.target.value})}
              maxLength={100}
            />
          </div>
          <div className="form-group">
            <label>Stat 1 Value</label>
            <input
              type="text"
              value={hero.stat_open_value}
              onChange={(e) => setHero({...hero, stat_open_value: e.target.value})}
              maxLength={50}
            />
          </div>
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label>Stat 2 Label</label>
            <input
              type="text"
              value={hero.stat_matches_label}
              onChange={(e) => setHero({...hero, stat_matches_label: e.target.value})}
              maxLength={100}
            />
          </div>
          <div className="form-group">
            <label>Stat 2 Value</label>
            <input
              type="text"
              value={hero.stat_matches_value}
              onChange={(e) => setHero({...hero, stat_matches_value: e.target.value})}
              maxLength={50}
            />
          </div>
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label>Stat 3 Label</label>
            <input
              type="text"
              value={hero.stat_courts_label}
              onChange={(e) => setHero({...hero, stat_courts_label: e.target.value})}
              maxLength={100}
            />
          </div>
          <div className="form-group">
            <label>Stat 3 Value</label>
            <input
              type="text"
              value={hero.stat_courts_value}
              onChange={(e) => setHero({...hero, stat_courts_value: e.target.value})}
              maxLength={50}
            />
          </div>
        </div>
      </div>
      
      <button type="submit" disabled={saving} className="btn btn-primary">
        {saving ? 'Saving...' : 'Save Changes'}
      </button>
    </form>
  );
}

export default HeroSectionEditor;
```

---

## Validation Rules

### Required Fields
- None (all fields are optional in PATCH, but should have defaults)

### Field Constraints
- `title_one`: Max 200 characters
- `title_two`: Max 200 characters
- `description`: No length limit
- `stat_*_label`: Max 100 characters each
- `stat_*_value`: Max 50 characters each

### Notes
- Empty title fields will fail validation
- Image is optional
- Stats have default values if not set

---

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "title_one": ["Title one cannot be empty."]
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
2. Find **"Get hero section content"** and **"Update hero section content"**
3. Click **"Try it out"**
4. For PATCH: Click "Authorize" and add your admin token
5. Fill in fields you want to update
6. Click **"Execute"**
7. View response

---

## Database Table

**Table Name:** `cms_herosection`

**Schema:**
```sql
CREATE TABLE cms_herosection (
    id INTEGER PRIMARY KEY,  -- Always 1 (singleton)
    title_one VARCHAR(200) NOT NULL,
    title_two VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    image VARCHAR(255),  -- Cloudinary URL
    stat_open_label VARCHAR(100) DEFAULT 'Open every day',
    stat_open_value VARCHAR(50) DEFAULT '7 Days/Week',
    stat_matches_label VARCHAR(100) DEFAULT 'Matches hosted',
    stat_matches_value VARCHAR(50) DEFAULT '500+',
    stat_courts_label VARCHAR(100) DEFAULT 'Premium courts',
    stat_courts_value VARCHAR(50) DEFAULT '2 Courts',
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## CSS Example

```css
.hero-section {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background-color: #1a1a2e;
  color: white;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(26, 26, 46, 0.9), rgba(0, 0, 0, 0.7));
  z-index: 1;
}

.hero-content {
  position: relative;
  z-index: 2;
  text-align: center;
  padding: 2rem;
  max-width: 1200px;
}

.hero-title {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  font-weight: 800;
  line-height: 1.2;
}

.title-line-1 {
  display: block;
  color: white;
}

.title-line-2 {
  display: block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.9;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-stats {
  display: flex;
  gap: 3rem;
  justify-content: center;
  margin: 3rem 0;
  flex-wrap: wrap;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.btn {
  padding: 1rem 2rem;
  font-size: 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background: white;
  color: #1a1a2e;
}
```

---

## Summary

✅ **Singleton model** created (HeroSection)  
✅ **GET endpoint** (public access)  
✅ **PATCH endpoint** (admin-only)  
✅ **Image upload** to Cloudinary  
✅ **3 structured stats** with labels and values  
✅ **Partial updates** supported  
✅ **Django admin** integration  
✅ **Swagger documentation** included  
✅ **Migration** created and applied  

**The Hero Section API is ready to use!** 🚀

**Test it at:** `http://localhost:8000/api/v1/docs/` → Look for "cms" tag → "homepage/hero-section"
