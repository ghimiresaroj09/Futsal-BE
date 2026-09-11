# CMS API Quick Reference

**All CMS endpoints are under:** `/api/v1/cms/`

---

## Hero Section (Singleton)

```
GET    /api/v1/cms/homepage/hero-section/     (public)
PATCH  /api/v1/cms/homepage/hero-section/     (admin)
```

**Response:**
```json
{
  "title_one": "Welcome to",
  "title_two": "Premium Futsal",
  "description": "...",
  "image_url": "https://...",
  "stats": [
    {"label": "Open every day", "value": "7 Days/Week"},
    {"label": "Matches hosted", "value": "500+"},
    {"label": "Premium courts", "value": "2 Courts"}
  ]
}
```

---

## Arena Section (Singleton)

```
GET    /api/v1/cms/homepage/arena/            (public)
PATCH  /api/v1/cms/homepage/arena/            (admin)
```

**Response:**
```json
{
  "title": "Premium Futsal Arena",
  "description": "World-class facilities...",
  "features": [
    "Professional turf",
    "LED lighting",
    "Climate controlled"
  ]
}
```

---

## Why Us Section (Singleton)

```
GET    /api/v1/cms/homepage/why-us/           (public)
PATCH  /api/v1/cms/homepage/why-us/           (admin)
```

**Response:**
```json
{
  "title": "Why Choose Us",
  "description": "Best futsal experience...",
  "features": [
    {
      "iconcode": "trophy",
      "title": "Professional Grade",
      "description": "International standard facilities"
    },
    {
      "iconcode": "clock",
      "title": "24/7 Booking",
      "description": "Book anytime online"
    }
  ]
}
```

---

## Carousel Images (Collection)

```
GET    /api/v1/cms/homepage/carousel/         (public - active only)
POST   /api/v1/cms/homepage/carousel/         (admin)
GET    /api/v1/cms/homepage/carousel/{id}/    (public)
PATCH  /api/v1/cms/homepage/carousel/{id}/    (admin)
DELETE /api/v1/cms/homepage/carousel/{id}/    (admin)
```

**Response:**
```json
{
  "id": "uuid",
  "image_url": "https://...",
  "alt_text": "Description",
  "sort_order": 1,
  "is_active": true
}
```

---

## Testimonials (Collection)

```
GET    /api/v1/cms/testimonials/              (public - active only)
POST   /api/v1/cms/testimonials/              (admin)
GET    /api/v1/cms/testimonials/{id}/         (public)
PATCH  /api/v1/cms/testimonials/{id}/         (admin)
DELETE /api/v1/cms/testimonials/{id}/         (admin)
```

**Response:**
```json
{
  "id": "uuid",
  "full_name": "John Doe",
  "title": "Regular Player",
  "image_url": "https://...",
  "content": "Great facilities!",
  "sort_order": 1,
  "is_active": true
}
```

---

## Authentication

**Public endpoints:** No auth required  
**Admin endpoints:** `Authorization: Bearer YOUR_TOKEN`

---

## Quick Frontend Load

```javascript
// Load all CMS content
const loadCMS = async () => {
  const [hero, arena, whyUs, carousel, testimonials] = await Promise.all([
    fetch('/api/v1/cms/homepage/hero-section/').then(r => r.json()),
    fetch('/api/v1/cms/homepage/arena/').then(r => r.json()),
    fetch('/api/v1/cms/homepage/why-us/').then(r => r.json()),
    fetch('/api/v1/cms/homepage/carousel/').then(r => r.json()),
    fetch('/api/v1/cms/testimonials/').then(r => r.json())
  ]);
  
  return {
    hero: hero.data,
    arena: arena.data,
    whyUs: whyUs.data,
    carousel: carousel.data.results,
    testimonials: testimonials.data.results
  };
};
```

---

## Quick Admin Update

```javascript
// Update hero section
await fetch('/api/v1/cms/homepage/hero-section/', {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    title_one: "New Title"
  })
});

// Update arena features
await fetch('/api/v1/cms/homepage/arena/', {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    features: ["Feature 1", "Feature 2", "Feature 3"]
  })
});

// Update why us features
await fetch('/api/v1/cms/homepage/why-us/', {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    features: [
      {
        iconcode: "trophy",
        title: "Award Winning",
        description: "Best in class"
      },
      {
        iconcode: "star",
        title: "5-Star Rated",
        description: "Top customer ratings"
      }
    ]
  })
});

// Upload carousel image
const formData = new FormData();
formData.append('image', file);
formData.append('alt_text', 'Image description');
formData.append('sort_order', 1);

await fetch('/api/v1/cms/homepage/carousel/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

---

## Test Everything

**Swagger UI:** `http://localhost:8000/api/v1/docs/`  
**Look for:** "cms" tag

---

✅ All 5 CMS components ready to use!
