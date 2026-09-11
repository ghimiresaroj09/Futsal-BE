# Why Us Section API Documentation

## Overview

REST API for managing the homepage "Why Choose Us" section with title, description, and an array of feature objects. Each feature contains an icon code, title, and description. This is a singleton endpoint - only one why us section exists.

**Base URL:** `/api/v1/cms/homepage/why-us/`

**Date Created:** September 11, 2026

---

## Features

✅ **Singleton pattern** (only one why us section)  
✅ **JSON array of feature objects** (flexible structured data)  
✅ **Icon support** (iconcode field for icon libraries like FontAwesome, Lucide, etc.)  
✅ **Object validation** (ensures each feature has iconcode, title, description)  
✅ **Public read access** (anyone can view)  
✅ **Admin-only write access** (update requires authentication)  
✅ **Automatic timestamps**  
✅ **Swagger documentation**  

---

## Database Model

```python
class WhyUsSection:
    title: CharField(max_length=200)
    description: TextField
    features: JSONField (array of objects)
    updated_at: DateTime (auto)

# Feature Object Structure:
{
    "iconcode": "string",    # Icon identifier (e.g., "trophy", "shield")
    "title": "string",       # Feature title
    "description": "string"  # Feature description
}
```

---

## API Endpoints

### 🔵 GET - Retrieve Why Us Section

**Endpoint:**
```
GET /api/v1/cms/homepage/why-us/
```

**Authentication:** None (Public)

**Description:** Returns the homepage why us section content including title, description, and features array with icon codes.

**Request Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/cms/homepage/why-us/"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Why us section retrieved successfully.",
  "data": {
    "title": "Why Choose Us",
    "description": "We offer the best futsal experience with world-class facilities, professional coaching, and a vibrant community of players.",
    "features": [
      {
        "iconcode": "trophy",
        "title": "Professional Grade Facilities",
        "description": "International standard courts with premium artificial turf and professional lighting systems."
      },
      {
        "iconcode": "clock",
        "title": "24/7 Online Booking",
        "description": "Book your slots anytime, anywhere with our easy-to-use online booking system."
      },
      {
        "iconcode": "shield",
        "title": "Safe & Secure",
        "description": "CCTV monitored premises with secure parking and professional staff on-site."
      },
      {
        "iconcode": "users",
        "title": "Vibrant Community",
        "description": "Join hundreds of players in tournaments, leagues, and friendly matches."
      },
      {
        "iconcode": "star",
        "title": "Expert Coaching",
        "description": "Professional coaches available for training sessions and skill development."
      },
      {
        "iconcode": "dollar-sign",
        "title": "Competitive Pricing",
        "description": "Affordable rates with flexible packages for regular players and teams."
      }
    ],
    "updated_at": "2026-09-11T18:47:00Z"
  }
}
```

**JavaScript Example:**
```javascript
const response = await fetch('/api/v1/cms/homepage/why-us/');
const result = await response.json();

console.log(result.data.title);              // "Why Choose Us"
console.log(result.data.features.length);    // 6
console.log(result.data.features[0].title);  // "Professional Grade Facilities"
```

---

### 🟡 PATCH - Update Why Us Section

**Endpoint:**
```
PATCH /api/v1/cms/homepage/why-us/
```

**Authentication:** Required (Admin only)

**Content-Type:** `application/json`

**Description:** Update the why us section content. Only include fields you want to change.

**Request Headers:**
```
Content-Type: application/json
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Request Body (all fields optional):**
```json
{
  "title": "Why Choose Premium Futsal",
  "description": "Updated description here...",
  "features": [
    {
      "iconcode": "trophy",
      "title": "Award Winning",
      "description": "Recognized as the best futsal venue in the region."
    },
    {
      "iconcode": "shield",
      "title": "Safe Environment",
      "description": "24/7 security and CCTV monitoring."
    }
  ]
}
```

**Field Reference:**
```json
{
  "title": "string (max 200 chars, optional)",
  "description": "string (optional)",
  "features": [
    {
      "iconcode": "string (required, non-empty)",
      "title": "string (required, non-empty)",
      "description": "string (required, non-empty)"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Why us section updated successfully.",
  "data": {
    "title": "Why Choose Premium Futsal",
    "description": "Updated description here...",
    "features": [
      {
        "iconcode": "trophy",
        "title": "Award Winning",
        "description": "Recognized as the best futsal venue in the region."
      },
      {
        "iconcode": "shield",
        "title": "Safe Environment",
        "description": "24/7 security and CCTV monitoring."
      }
    ],
    "updated_at": "2026-09-11T18:50:30Z"
  }
}
```

**cURL Example (Update all fields):**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/homepage/why-us/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "title": "Why Choose Us",
    "description": "The ultimate futsal experience",
    "features": [
      {
        "iconcode": "trophy",
        "title": "Premium Facilities",
        "description": "World-class infrastructure"
      },
      {
        "iconcode": "star",
        "title": "Expert Staff",
        "description": "Professional coaches and support"
      }
    ]
  }'
```

**cURL Example (Update only features):**
```bash
curl -X PATCH "http://localhost:8000/api/v1/cms/homepage/why-us/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "features": [
      {
        "iconcode": "check-circle",
        "title": "Quality Assured",
        "description": "ISO certified facilities"
      }
    ]
  }'
```

**JavaScript Example:**
```javascript
const updateWhyUs = async (updates) => {
  const response = await fetch('/api/v1/cms/homepage/why-us/', {
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
await updateWhyUs({
  title: "Why We're The Best"
});

// Update features array
await updateWhyUs({
  features: [
    {
      iconcode: "trophy",
      title: "Champions Choice",
      description: "Preferred by professional teams"
    },
    {
      iconcode: "heart",
      title: "Customer Focused",
      description: "Your satisfaction is our priority"
    }
  ]
});

// Update all fields
await updateWhyUs({
  title: "Why Choose Us",
  description: "Experience the difference",
  features: [
    { iconcode: "star", title: "5-Star Rated", description: "Highest customer ratings" }
  ]
});
```

---

## Frontend Integration

### React Example - Display Why Us Section

```jsx
import { useEffect, useState } from 'react';
import { 
  Trophy, Clock, Shield, Users, Star, DollarSign,
  CheckCircle, Heart, Award 
} from 'lucide-react';

// Icon mapping for Lucide icons
const iconMap = {
  'trophy': Trophy,
  'clock': Clock,
  'shield': Shield,
  'users': Users,
  'star': Star,
  'dollar-sign': DollarSign,
  'check-circle': CheckCircle,
  'heart': Heart,
  'award': Award,
};

function WhyUsSection() {
  const [whyUs, setWhyUs] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadWhyUsSection();
  }, []);
  
  const loadWhyUsSection = async () => {
    try {
      const response = await fetch('/api/v1/cms/homepage/why-us/');
      const result = await response.json();
      setWhyUs(result.data);
    } catch (error) {
      console.error('Failed to load why us section:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <div>Loading...</div>;
  if (!whyUs) return null;
  
  return (
    <section className="why-us-section">
      <div className="container">
        <h2 className="section-title">{whyUs.title}</h2>
        <p className="section-description">{whyUs.description}</p>
        
        <div className="features-grid">
          {whyUs.features.map((feature, index) => {
            const IconComponent = iconMap[feature.iconcode] || Star;
            
            return (
              <div key={index} className="feature-card">
                <div className="icon-wrapper">
                  <IconComponent className="feature-icon" size={40} />
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

export default WhyUsSection;
```

---

### React Example - Admin Edit Form

```jsx
import { useState, useEffect } from 'react';
import { Plus, X, Edit2 } from 'lucide-react';

function WhyUsEditForm() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [features, setFeatures] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Form state for new/editing feature
  const [editingIndex, setEditingIndex] = useState(null);
  const [featureForm, setFeatureForm] = useState({
    iconcode: '',
    title: '',
    description: ''
  });
  
  useEffect(() => {
    loadWhyUs();
  }, []);
  
  const loadWhyUs = async () => {
    const response = await fetch('/api/v1/cms/homepage/why-us/');
    const result = await response.json();
    
    setTitle(result.data.title);
    setDescription(result.data.description);
    setFeatures(result.data.features);
  };
  
  const addFeature = () => {
    if (featureForm.iconcode && featureForm.title && featureForm.description) {
      setFeatures([...features, { ...featureForm }]);
      setFeatureForm({ iconcode: '', title: '', description: '' });
    }
  };
  
  const updateFeature = () => {
    if (editingIndex !== null) {
      const updatedFeatures = [...features];
      updatedFeatures[editingIndex] = { ...featureForm };
      setFeatures(updatedFeatures);
      setEditingIndex(null);
      setFeatureForm({ iconcode: '', title: '', description: '' });
    }
  };
  
  const editFeature = (index) => {
    setEditingIndex(index);
    setFeatureForm({ ...features[index] });
  };
  
  const removeFeature = (index) => {
    setFeatures(features.filter((_, i) => i !== index));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch('/api/v1/cms/homepage/why-us/', {
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
        alert('Why us section updated successfully!');
      } else {
        alert('Failed to update why us section');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="why-us-edit-form">
      <h3>Edit Why Us Section</h3>
      
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
              <div className="feature-content">
                <span className="icon-badge">{feature.iconcode}</span>
                <div>
                  <strong>{feature.title}</strong>
                  <p>{feature.description}</p>
                </div>
              </div>
              <div className="feature-actions">
                <button
                  type="button"
                  onClick={() => editFeature(index)}
                  className="btn-edit"
                >
                  <Edit2 size={16} />
                </button>
                <button
                  type="button"
                  onClick={() => removeFeature(index)}
                  className="btn-remove"
                >
                  <X size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
        
        <div className="add-feature-form">
          <h4>{editingIndex !== null ? 'Edit Feature' : 'Add Feature'}</h4>
          
          <input
            type="text"
            placeholder="Icon code (e.g., trophy, star, shield)"
            value={featureForm.iconcode}
            onChange={(e) => setFeatureForm({...featureForm, iconcode: e.target.value})}
          />
          
          <input
            type="text"
            placeholder="Feature title"
            value={featureForm.title}
            onChange={(e) => setFeatureForm({...featureForm, title: e.target.value})}
          />
          
          <textarea
            placeholder="Feature description"
            value={featureForm.description}
            onChange={(e) => setFeatureForm({...featureForm, description: e.target.value})}
            rows={3}
          />
          
          {editingIndex !== null ? (
            <div className="button-group">
              <button type="button" onClick={updateFeature} className="btn-primary">
                Update Feature
              </button>
              <button 
                type="button" 
                onClick={() => {
                  setEditingIndex(null);
                  setFeatureForm({ iconcode: '', title: '', description: '' });
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button type="button" onClick={addFeature} className="btn-add">
              <Plus size={16} /> Add Feature
            </button>
          )}
        </div>
      </div>
      
      <button type="submit" disabled={loading} className="btn btn-primary">
        {loading ? 'Saving...' : 'Save Changes'}
      </button>
    </form>
  );
}

export default WhyUsEditForm;
```

---

### Vue.js Example - Display Why Us

```vue
<template>
  <section v-if="whyUs" class="why-us-section">
    <div class="container">
      <h2>{{ whyUs.title }}</h2>
      <p>{{ whyUs.description }}</p>
      
      <div class="features-grid">
        <div 
          v-for="(feature, index) in whyUs.features" 
          :key="index"
          class="feature-card"
        >
          <div class="icon-wrapper">
            <i :class="`icon-${feature.iconcode}`"></i>
          </div>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  data() {
    return {
      whyUs: null
    };
  },
  
  mounted() {
    this.loadWhyUs();
  },
  
  methods: {
    async loadWhyUs() {
      try {
        const response = await fetch('/api/v1/cms/homepage/why-us/');
        const result = await response.json();
        this.whyUs = result.data;
      } catch (error) {
        console.error('Failed to load why us:', error);
      }
    }
  }
};
</script>
```

---

## Icon Libraries Integration

### Using FontAwesome Icons

```jsx
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faTrophy, faClock, faShield, faUsers, faStar, faDollarSign 
} from '@fortawesome/free-solid-svg-icons';

const iconMap = {
  'trophy': faTrophy,
  'clock': faClock,
  'shield': faShield,
  'users': faUsers,
  'star': faStar,
  'dollar-sign': faDollarSign,
};

function FeatureCard({ feature }) {
  const icon = iconMap[feature.iconcode] || faStar;
  
  return (
    <div className="feature-card">
      <FontAwesomeIcon icon={icon} size="3x" />
      <h3>{feature.title}</h3>
      <p>{feature.description}</p>
    </div>
  );
}
```

---

### Using Heroicons

```jsx
import {
  TrophyIcon, ClockIcon, ShieldCheckIcon, 
  UsersIcon, StarIcon
} from '@heroicons/react/24/outline';

const iconMap = {
  'trophy': TrophyIcon,
  'clock': ClockIcon,
  'shield': ShieldCheckIcon,
  'users': UsersIcon,
  'star': StarIcon,
};

function FeatureCard({ feature }) {
  const Icon = iconMap[feature.iconcode] || StarIcon;
  
  return (
    <div className="feature-card">
      <Icon className="w-12 h-12" />
      <h3>{feature.title}</h3>
      <p>{feature.description}</p>
    </div>
  );
}
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
- Each item must be an object
- Each object must have: `iconcode`, `title`, `description`
- All fields in object must be non-empty strings

**Valid Feature Object:**
```json
{
  "iconcode": "trophy",
  "title": "Award Winning",
  "description": "Best in class service"
}
```

**Invalid Examples:**
```json
// ❌ Missing required field
{
  "iconcode": "trophy",
  "title": "Award Winning"
}

// ❌ Empty string
{
  "iconcode": "",
  "title": "Award Winning",
  "description": "Best in class"
}

// ❌ Not an object
"trophy"

// ❌ Wrong data type
{
  "iconcode": 123,
  "title": "Award Winning",
  "description": "Best in class"
}
```

---

## Error Responses

### 400 Bad Request (Validation Error)
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "title": ["Title cannot be empty."]
  }
}
```

### 400 Bad Request (Invalid Features Array)
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "features": ["Features must be an array."]
  }
}
```

### 400 Bad Request (Invalid Feature Object)
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "features": ["Feature at index 0 must be an object."]
  }
}
```

### 400 Bad Request (Missing Required Field)
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "features": ["Feature at index 1 is missing required field: 'title'."]
  }
}
```

### 400 Bad Request (Empty String in Field)
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "features": ["Feature at index 0: 'iconcode' cannot be empty."]
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

## CSS Example for Why Us Section

```css
.why-us-section {
  padding: 80px 0;
  background: #f8f9fa;
}

.why-us-section .container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-title {
  font-size: 2.5rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 20px;
  color: #1a202c;
}

.section-description {
  font-size: 1.1rem;
  text-align: center;
  max-width: 700px;
  margin: 0 auto 60px;
  color: #4a5568;
  line-height: 1.7;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 30px;
  margin-top: 40px;
}

.feature-card {
  background: white;
  padding: 40px 30px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  color: white;
}

.feature-icon {
  width: 40px;
  height: 40px;
}

.feature-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 15px;
  color: #2d3748;
}

.feature-card p {
  font-size: 1rem;
  color: #718096;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .section-title {
    font-size: 2rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
}
```

---

## Common Icon Codes

### Recommended Icon Codes (Lucide/FontAwesome Compatible)

**Success & Quality:**
- `trophy` - Awards, achievement
- `star` - Featured, premium
- `check-circle` - Verified, approved
- `award` - Recognition

**Security & Trust:**
- `shield` - Security, protection
- `lock` - Secure, privacy
- `shield-check` - Verified security

**Time & Availability:**
- `clock` - 24/7, timing
- `calendar` - Scheduling
- `zap` - Fast, instant

**People & Community:**
- `users` - Community, team
- `heart` - Love, care
- `thumbs-up` - Approval, satisfaction

**Money & Value:**
- `dollar-sign` - Pricing, value
- `tag` - Deals, offers
- `trending-up` - Growth, improvement

**Location & Facility:**
- `map-pin` - Location
- `home` - Facility
- `building` - Infrastructure

---

## Testing with Swagger

Access Swagger UI at: `http://localhost:8000/api/v1/docs/`

1. Navigate to **"cms"** tag
2. Find `/api/v1/cms/homepage/why-us/` endpoints
3. **GET** - Click "Try it out" → "Execute" (no auth needed)
4. **PATCH** - Click "Authorize" → Add admin token → "Try it out" → Edit request body → "Execute"

---

## Common Use Cases

### 1. Initial Setup (Admin)
```javascript
// Set up why us section for the first time
const setupWhyUs = async () => {
  await fetch('/api/v1/cms/homepage/why-us/', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${adminToken}`
    },
    body: JSON.stringify({
      title: "Why Choose Us",
      description: "Experience the difference at our premium futsal facility",
      features: [
        {
          iconcode: "trophy",
          title: "Professional Grade",
          description: "International standard facilities and equipment"
        },
        {
          iconcode: "clock",
          title: "24/7 Booking",
          description: "Book anytime with our easy online system"
        },
        {
          iconcode: "shield",
          title: "Safe & Secure",
          description: "CCTV monitored with professional security"
        }
      ]
    })
  });
};
```

### 2. Add New Feature
```javascript
// Load current data, add feature, update
const addFeature = async (newFeature) => {
  const response = await fetch('/api/v1/cms/homepage/why-us/');
  const result = await response.json();
  
  const updatedFeatures = [...result.data.features, newFeature];
  
  await fetch('/api/v1/cms/homepage/why-us/', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${adminToken}`
    },
    body: JSON.stringify({ features: updatedFeatures })
  });
};

// Usage
await addFeature({
  iconcode: "star",
  title: "5-Star Rated",
  description: "Highest customer satisfaction ratings"
});
```

### 3. Update Specific Feature
```javascript
// Update feature at specific index
const updateFeature = async (index, updatedFeature) => {
  const response = await fetch('/api/v1/cms/homepage/why-us/');
  const result = await response.json();
  
  const features = [...result.data.features];
  features[index] = updatedFeature;
  
  await fetch('/api/v1/cms/homepage/why-us/', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${adminToken}`
    },
    body: JSON.stringify({ features })
  });
};
```

### 4. Remove Feature
```javascript
// Remove feature at specific index
const removeFeature = async (index) => {
  const response = await fetch('/api/v1/cms/homepage/why-us/');
  const result = await response.json();
  
  const updatedFeatures = result.data.features.filter((_, i) => i !== index);
  
  await fetch('/api/v1/cms/homepage/why-us/', {
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

✅ **WhyUsSection model** created (singleton)  
✅ **GET/PATCH API** endpoints  
✅ **JSONField for features** array of objects  
✅ **Public read access**  
✅ **Admin write access**  
✅ **Object validation** (iconcode, title, description required)  
✅ **Django admin panel** integration  
✅ **Swagger documentation**  
✅ **Migration** created and applied  

**The Why Us Section API is ready to use!** 🚀

**Test it at:** `http://localhost:8000/api/v1/docs/` → Look for "cms" tag → "homepage/why-us"

---

**Last Updated:** September 11, 2026  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
