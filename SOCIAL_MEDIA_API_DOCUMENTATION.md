# Social Media Links API Documentation

## Overview
Social media profile links are integrated into the Futsal venue model. Admins can configure links to Facebook, Instagram, Twitter/X, and TikTok profiles directly through the main futsal endpoint.

**Base URL**: `/api/v1/futsal/`

**Authentication**: 
- Public: Read access (GET)
- Admin: Update access (PATCH)

---

## Model Schema

### Futsal Model (includes social media fields)
The Futsal model now includes social media fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | String | Yes | Futsal venue name |
| `description` | Text | No | Venue description |
| `location` | String | Yes | Location |
| `address` | String | No | Full address |
| `phone` | String | No | Phone number |
| `email` | Email | No | Email address |
| `price_per_slot` | Decimal | Yes | Price per slot |
| `slot_duration` | Integer | Yes | Slot duration (minutes) |
| `opening_time` | Time | Yes | Opening time |
| `closing_time` | Time | Yes | Closing time |
| `status` | String | Yes | Venue status (ACTIVE/INACTIVE) |
| **`facebook`** | **String (URL)** | **No** | **Facebook page URL** |
| **`instagram`** | **String (URL)** | **No** | **Instagram profile URL** |
| **`twitter`** | **String (URL)** | **No** | **Twitter/X profile URL** |
| **`tiktok`** | **String (URL)** | **No** | **TikTok profile URL** |
| `created_at` | DateTime | Auto | Creation timestamp |
| `updated_at` | DateTime | Auto | Last update timestamp |

**Notes**:
- Social media fields are optional (can be empty strings)
- URLs are validated to ensure they contain the appropriate domain
- Part of the singleton Futsal model

---

## Endpoints

### 1. Get Futsal Details (including Social Media)
**GET** `/api/v1/futsal/`

Returns the futsal venue details including social media links. Public access.

**Response:** `200 OK`
```json
{
  "status": "success",
  "message": "Data retrieved successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Elite Futsal Arena",
    "description": "Premium futsal facility",
    "location": "Downtown",
    "address": "123 Main Street",
    "phone": "+1234567890",
    "email": "info@futsal.com",
    "price_per_slot": "50.00",
    "slot_duration": 60,
    "opening_time": "06:00:00",
    "closing_time": "22:00:00",
    "status": "ACTIVE",
    "facebook": "https://facebook.com/futsalarena",
    "instagram": "https://instagram.com/futsalarena",
    "twitter": "https://twitter.com/futsalarena",
    "tiktok": "https://tiktok.com/@futsalarena",
    "created_at": "2026-09-01T10:00:00Z",
    "updated_at": "2026-09-10T15:30:00Z"
  }
}
```

**Empty Social Links Response:**
```json
{
  "status": "success",
  "message": "Data retrieved successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Elite Futsal Arena",
    ...
    "facebook": "",
    "instagram": "",
    "twitter": "",
    "tiktok": "",
    ...
  }
}
```

---

### 2. Update Futsal Details (including Social Media)
**PATCH** `/api/v1/futsal/`

Update futsal venue details including social media links. **Admin only**.

**Request:** `application/json`

Update only social media fields:
```json
{
  "facebook": "https://facebook.com/futsalarena",
  "instagram": "https://instagram.com/futsalarena",
  "twitter": "https://x.com/futsalarena",
  "tiktok": "https://tiktok.com/@futsalarena"
}
```

Update any futsal fields including social media:
```json
{
  "name": "Elite Futsal Arena",
  "phone": "+1234567890",
  "instagram": "https://instagram.com/newfutsalarena"
}
```

**Partial Update (any fields):**
```json
{
  "instagram": "https://instagram.com/newfutsalarena"
}
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "message": "Futsal details updated successfully.",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Elite Futsal Arena",
    ...
    "facebook": "https://facebook.com/futsalarena",
    "instagram": "https://instagram.com/newfutsalarena",
    "twitter": "https://x.com/futsalarena",
    "tiktok": "https://tiktok.com/@futsalarena",
    "updated_at": "2026-09-10T16:00:00Z"
  }
}
```

**Clear a Link (set to empty):**
```json
{
  "tiktok": ""
}
```

---

## Validation Rules

### Facebook URL
- Must contain `facebook.com` or `fb.com`
- Examples:
  - ✅ `https://facebook.com/futsalarena`
  - ✅ `https://www.facebook.com/futsalarena`
  - ✅ `https://fb.com/futsalarena`
  - ❌ `https://someother.com/page`

### Instagram URL
- Must contain `instagram.com`
- Examples:
  - ✅ `https://instagram.com/futsalarena`
  - ✅ `https://www.instagram.com/futsalarena`
  - ❌ `https://twitter.com/futsalarena`

### Twitter/X URL
- Must contain `twitter.com` or `x.com`
- Examples:
  - ✅ `https://twitter.com/futsalarena`
  - ✅ `https://x.com/futsalarena`
  - ✅ `https://www.twitter.com/futsalarena`
  - ❌ `https://instagram.com/futsalarena`

### TikTok URL
- Must contain `tiktok.com`
- Examples:
  - ✅ `https://tiktok.com/@futsalarena`
  - ✅ `https://www.tiktok.com/@futsalarena`
  - ❌ `https://youtube.com/@futsalarena`

---

## Error Responses

### Validation Error
**Status:** `400 Bad Request`
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "facebook": ["Please provide a valid Facebook URL."],
    "instagram": ["Please provide a valid Instagram URL."]
  }
}
```

### Invalid URL Format
**Status:** `400 Bad Request`
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "twitter": ["Enter a valid URL."]
  }
}
```

### Unauthorized (Non-Admin trying to update)
**Status:** `403 Forbidden`
```json
{
  "status": "error",
  "message": "You do not have permission to perform this action."
}
```

---

## Usage Examples

### Example 1: Get Futsal Details with Social Links (Public)
```bash
curl "http://localhost:8000/api/v1/futsal/"
```

### Example 2: Update All Social Links (Admin)
```bash
curl -X PATCH "http://localhost:8000/api/v1/futsal/" \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "facebook": "https://facebook.com/futsalarena",
    "instagram": "https://instagram.com/futsalarena",
    "twitter": "https://twitter.com/futsalarena",
    "tiktok": "https://tiktok.com/@futsalarena"
  }'
```

### Example 3: Update Only Instagram (Admin)
```bash
curl -X PATCH "http://localhost:8000/api/v1/futsal/" \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "instagram": "https://instagram.com/newfutsalarena"
  }'
```

### Example 4: Remove TikTok Link (Admin)
```bash
curl -X PATCH "http://localhost:8000/api/v1/futsal/" \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "tiktok": ""
  }'
```

### Example 5: Update Venue Info and Social Links Together (Admin)
```bash
curl -X PATCH "http://localhost:8000/api/v1/futsal/" \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "email": "contact@futsal.com",
    "twitter": "https://x.com/futsalarena"
  }'
```

---

## Frontend Integration

### Fetch Futsal Details with Social Links
```javascript
// Get futsal details including social media links (public)
const response = await fetch('/api/v1/futsal/');
const { data } = await response.json();

// Access all fields
console.log('Venue:', data.name);
console.log('Phone:', data.phone);

// Display social links
if (data.facebook) {
  console.log('Facebook:', data.facebook);
}
if (data.instagram) {
  console.log('Instagram:', data.instagram);
}
```

### Update Social Links (Admin)
```javascript
const response = await fetch('/api/v1/futsal/', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    facebook: 'https://facebook.com/futsalarena',
    instagram: 'https://instagram.com/futsalarena'
  })
});

const result = await response.json();
console.log(result.message);
```

### React Component Example
```jsx
import { useState, useEffect } from 'react';

function FutsalInfo() {
  const [futsal, setFutsal] = useState(null);
  
  useEffect(() => {
    fetch('/api/v1/futsal/')
      .then(res => res.json())
      .then(result => setFutsal(result.data));
  }, []);
  
  if (!futsal) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>{futsal.name}</h1>
      <p>{futsal.description}</p>
      <p>Phone: {futsal.phone}</p>
      <p>Email: {futsal.email}</p>
      
      <div className="social-links">
        {futsal.facebook && (
          <a href={futsal.facebook} target="_blank" rel="noopener noreferrer">
            <i className="fab fa-facebook"></i>
          </a>
        )}
        {futsal.instagram && (
          <a href={futsal.instagram} target="_blank" rel="noopener noreferrer">
            <i className="fab fa-instagram"></i>
          </a>
        )}
        {futsal.twitter && (
          <a href={futsal.twitter} target="_blank" rel="noopener noreferrer">
            <i className="fab fa-twitter"></i>
          </a>
        )}
        {futsal.tiktok && (
          <a href={futsal.tiktok} target="_blank" rel="noopener noreferrer">
            <i className="fab fa-tiktok"></i>
          </a>
        )}
      </div>
    </div>
  );
}
```

---

## Admin Panel

Social media links are manageable via Django Admin at `/admin/futsal/futsal/`.

**Features**:
- Integrated with futsal venue editing
- Social Media section (collapsible)
- URL validation on save
- All fields optional
- Shows last updated timestamp

---

## Permissions

| Action | Public | Authenticated User | Admin |
|--------|--------|-------------------|-------|
| Get Links | ✅ | ✅ | ✅ |
| Update Links | ❌ | ❌ | ✅ |

---

## Technical Notes

1. **Integrated with Futsal Model**: Social media fields are part of the main Futsal model, not a separate table
2. **URL Validation**: Built-in Django `URLValidator` ensures proper URL format
3. **Domain Validation**: Custom validators ensure URLs match the expected platform
4. **Optional Fields**: All social media fields can be empty - only populate what you use
5. **Single Venue System**: Only one futsal venue exists, so social links are singleton by nature
6. **No Separate Endpoint**: Social media is accessed through `/api/v1/futsal/` not a separate route

---

## Database Schema

```sql
ALTER TABLE futsal_futsal 
ADD COLUMN facebook VARCHAR(200) DEFAULT '',
ADD COLUMN instagram VARCHAR(200) DEFAULT '',
ADD COLUMN twitter VARCHAR(200) DEFAULT '',
ADD COLUMN tiktok VARCHAR(200) DEFAULT '';
```

The social media fields are part of the `futsal_futsal` table.

---

## Common Use Cases

### Use Case 1: Footer Social Icons
Display social icons in website footer that link to your profiles.

### Use Case 2: Contact Page
Show all available social media channels on the contact page.

### Use Case 3: Share Prompts
Use social links to create "Follow us on X" calls-to-action.

### Use Case 4: Admin Management
Centralized location for admins to update social media URLs without code changes.

---

## Integration with Other APIs

Social media links are now part of the main futsal details, accessible alongside:
- **Futsal Details**: `/api/v1/futsal/` - Main venue information (includes social media)
- **Slots**: `/api/v1/slots/` - Available time slots
- **Futsal Media**: `/api/v1/futsal-media/` - Gallery images and videos
- **Contact**: `/api/v1/contact/` - Contact form submissions
- **CMS**: `/api/v1/cms/` - Website content management

---

## Best Practices

1. **Use Full URLs**: Always include `https://` in URLs
2. **Verify Links**: Test URLs before saving to ensure they're valid
3. **Keep Updated**: Regularly check that social links aren't broken
4. **Optional Fields**: Only populate the platforms you actively use
5. **Consistent Branding**: Use the same handle/username across platforms when possible

---

## Migration Info

**Migration Files**: 
- `futsal/migrations/0005_socialmedia.py` - Created separate SocialMedia model (deprecated)
- `futsal/migrations/0006_delete_socialmedia_futsal_facebook_futsal_instagram_and_more.py` - Moved to Futsal model

**Applied**: Yes
**Dependencies**: Previous futsal migrations

---

## Testing Checklist

- [ ] Get futsal details including social links (public access)
- [ ] Update Facebook link (admin)
- [ ] Update Instagram link (admin)
- [ ] Update Twitter/X link (admin)
- [ ] Update TikTok link (admin)
- [ ] Update multiple social links at once
- [ ] Update venue info and social links together
- [ ] Clear a link (set to empty)
- [ ] Verify URL validation (invalid URL format)
- [ ] Verify domain validation (wrong platform domain)
- [ ] Test unauthorized update attempt (non-admin)
- [ ] Verify admin panel shows social media fields
- [ ] Check updated_at timestamp changes

---

**Last Updated**: September 10, 2026
**API Version**: v1
**Status**: ✅ Complete and Deployed
