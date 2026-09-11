# Slot Generation Fix - Opening/Closing Time Validation

## Issue Summary

**Error:** 500 Internal Server Error when calling `/api/v1/admin/slots/generate/`

**Root Cause:** The Futsal singleton record in production database was missing `opening_time` and/or `closing_time` values, causing `datetime.combine()` to fail with `None` values.

**Date Fixed:** September 11, 2026

---

## The Problem

### Error Scenario

**Request:**
```bash
POST /api/v1/admin/slots/generate/
{
  "start_date": "2026-09-12",
  "end_date": "2026-09-20"
}
```

**Response:** 500 Internal Server Error

**Root Cause in Code:**
```python
# futsal/services.py - Line causing error
cursor = dt.datetime.combine(date, futsal.opening_time)  # ❌ futsal.opening_time is None
closing = dt.datetime.combine(date, futsal.closing_time)  # ❌ futsal.closing_time is None
```

**Python Error:**
```python
TypeError: combine() argument 2 must be datetime.time, not None
```

### Why This Happened

1. The Futsal model has `opening_time` and `closing_time` as **required fields** (not nullable)
2. However, the production database might have been created before these validations were in place
3. Or manual database changes set these values to `NULL`
4. Django allows `NULL` at the database level even if the model field doesn't have `null=True`

---

## The Solution

### 1. Added Validation in Service Layer ✅

**File:** `futsal/services.py`

**Change:** Added validation to check if opening/closing times are set before generating slots

```python
@transaction.atomic
def generate_slots_for_date(*, date: dt.date, futsal: Futsal | None = None) -> list[Slot]:
    """Generate whole-hour slots between the futsal opening and closing time."""
    futsal = futsal or Futsal.objects.get_solo()
    
    # ✅ NEW: Validate opening and closing times are set
    if not futsal.opening_time or not futsal.closing_time:
        error_msg = "Futsal opening_time and closing_time must be configured before generating slots."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # ... rest of the code
```

**Benefits:**
- ✅ Clear error message instead of cryptic 500 error
- ✅ Helps identify configuration issues
- ✅ Prevents database errors

---

### 2. Added Error Handling in View ✅

**File:** `futsal/views.py`

**Change:** Added try-catch to return user-friendly error

```python
def generate(self, request):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        created = generate_slots_for_range(
            start_date=serializer.validated_data["start_date"],
            end_date=serializer.validated_data["end_date"],
        )
        return success_response(
            data={"created": len(created), "slots": SlotSerializer(created, many=True).data},
            message=f"{len(created)} slot(s) generated successfully.",
            status=status.HTTP_201_CREATED,
        )
    except ValueError as e:
        # ✅ NEW: Handle configuration errors gracefully
        return success_response(
            data={"created": 0, "slots": []},
            message=str(e),
            status=status.HTTP_400_BAD_REQUEST,
        )
```

**Benefits:**
- ✅ Returns 400 Bad Request instead of 500 Internal Server Error
- ✅ Clear error message in response
- ✅ Admin knows what needs to be fixed

---

### 3. Created Data Migration ✅

**File:** `futsal/migrations/0004_ensure_futsal_hours.py`

**Purpose:** Automatically set default opening/closing times if missing

```python
def ensure_futsal_hours(apps, schema_editor):
    """Ensure Futsal singleton has opening and closing times set."""
    Futsal = apps.get_model('futsal', 'Futsal')
    
    # Get or create the singleton
    futsal = Futsal.objects.first()
    if not futsal:
        # Create singleton with default times
        Futsal.objects.create(
            name="Futsal Arena",
            opening_time=dt.time(6, 0),  # 6:00 AM
            closing_time=dt.time(22, 0),  # 10:00 PM
            price_per_slot=1500,
            slot_duration=60,
        )
    else:
        # Update existing singleton if times are missing
        updated = False
        if not futsal.opening_time:
            futsal.opening_time = dt.time(6, 0)
            updated = True
        if not futsal.closing_time:
            futsal.closing_time = dt.time(22, 0)
            updated = True
        if updated:
            futsal.save(update_fields=['opening_time', 'closing_time'])
```

**Benefits:**
- ✅ Automatically fixes the issue on deployment
- ✅ Sets sensible defaults (6 AM - 10 PM)
- ✅ Safe to run multiple times (idempotent)

---

## API Responses After Fix

### Scenario 1: Times Are Set (Normal Operation)

**Request:**
```bash
POST /api/v1/admin/slots/generate/
{
  "start_date": "2026-09-12",
  "end_date": "2026-09-20"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "144 slot(s) generated successfully.",
  "data": {
    "created": 144,
    "slots": [
      {
        "id": "uuid-1",
        "date": "2026-09-12",
        "start_time": "06:00:00",
        "end_time": "07:00:00",
        "price": "1500.00",
        "status": "AVAILABLE"
      }
      // ... more slots
    ]
  }
}
```

---

### Scenario 2: Times Are Missing (Configuration Error)

**Request:**
```bash
POST /api/v1/admin/slots/generate/
{
  "start_date": "2026-09-12",
  "end_date": "2026-09-20"
}
```

**Response (400 Bad Request):**
```json
{
  "status": "success",
  "message": "Futsal opening_time and closing_time must be configured before generating slots.",
  "data": {
    "created": 0,
    "slots": []
  }
}
```

**Frontend Display:**
```
⚠️ Configuration Error

Futsal opening_time and closing_time must be configured 
before generating slots.

Please update the futsal settings in the admin panel:
1. Go to Admin Panel → Futsal Settings
2. Set Opening Time (e.g., 06:00 AM)
3. Set Closing Time (e.g., 10:00 PM)
4. Save and try again
```

---

## How to Fix Manually (If Migration Doesn't Run)

### Option 1: Django Admin Panel

1. Go to: `https://futsal-be.onrender.com/admin/futsal/futsal/`
2. Click on the Futsal record
3. Set **Opening Time**: `06:00:00`
4. Set **Closing Time**: `22:00:00`
5. Click **Save**

---

### Option 2: Django Shell

```bash
python manage.py shell
```

```python
from futsal.models import Futsal
import datetime as dt

futsal = Futsal.objects.get_solo()
futsal.opening_time = dt.time(6, 0)   # 6:00 AM
futsal.closing_time = dt.time(22, 0)  # 10:00 PM
futsal.save()

print("Futsal hours updated!")
print(f"Opening: {futsal.opening_time}")
print(f"Closing: {futsal.closing_time}")
```

---

### Option 3: Direct SQL (Last Resort)

```sql
-- Check current values
SELECT id, name, opening_time, closing_time FROM futsal_futsal;

-- Update if NULL
UPDATE futsal_futsal 
SET 
  opening_time = '06:00:00',
  closing_time = '22:00:00'
WHERE opening_time IS NULL OR closing_time IS NULL;
```

---

## Deployment Steps

### For Production (Render.com)

1. **Commit and Push Changes:**
```bash
git add .
git commit -m "Fix: Add validation and migration for futsal opening/closing times"
git push origin main
```

2. **Deploy to Render:**
   - Render will automatically detect the new migration
   - Migration will run during deployment
   - If Futsal record exists with NULL times, they'll be set to defaults

3. **Verify After Deployment:**
```bash
# Check admin panel
https://futsal-be.onrender.com/admin/futsal/futsal/

# Or test the endpoint
POST https://futsal-be.onrender.com/api/v1/admin/slots/generate/
{
  "start_date": "2026-09-12",
  "end_date": "2026-09-13"
}
```

---

## Testing Locally

### Test 1: Generate Slots (Normal)

```bash
# With proper opening/closing times set
POST http://localhost:8000/api/v1/admin/slots/generate/
{
  "start_date": "2026-09-12",
  "end_date": "2026-09-13"
}

Expected: 201 Created with slots generated
```

### Test 2: Generate Slots (Missing Times - Simulated)

```python
# In Django shell
from futsal.models import Futsal

futsal = Futsal.objects.get_solo()
futsal.opening_time = None
futsal.closing_time = None
futsal.save()
```

```bash
POST http://localhost:8000/api/v1/admin/slots/generate/
{
  "start_date": "2026-09-12",
  "end_date": "2026-09-13"
}

Expected: 400 Bad Request with clear error message
```

### Test 3: Migration

```bash
# Run migration
python manage.py migrate futsal

# Check in shell
python manage.py shell
>>> from futsal.models import Futsal
>>> futsal = Futsal.objects.get_solo()
>>> print(futsal.opening_time)  # Should be 06:00:00
>>> print(futsal.closing_time)  # Should be 22:00:00
```

---

## What Each Hour Generates

Based on default times (6 AM - 10 PM):

```
Opening: 06:00 AM
Closing: 10:00 PM (22:00)
Duration: 1 hour per slot

Slots per day: 16 slots
- 06:00-07:00
- 07:00-08:00
- 08:00-09:00
- 09:00-10:00
- 10:00-11:00
- 11:00-12:00
- 12:00-13:00
- 13:00-14:00
- 14:00-15:00
- 15:00-16:00
- 16:00-17:00
- 17:00-18:00
- 18:00-19:00
- 19:00-20:00
- 20:00-21:00
- 21:00-22:00

Total for 9 days (Sep 12-20): 144 slots
```

---

## Prevention for Future

### Model Validation

The Futsal model already has validation in `clean()`:

```python
def clean(self):
    super().clean()
    if self.opening_time and self.closing_time and self.opening_time >= self.closing_time:
        raise ValidationError({"closing_time": "Closing time must be after opening time."})
```

### API Validation

The service function now validates before processing:

```python
if not futsal.opening_time or not futsal.closing_time:
    raise ValueError("Futsal opening_time and closing_time must be configured.")
```

### Migration

The migration ensures defaults are set:

```python
# Sets 6 AM - 10 PM if NULL
futsal.opening_time = dt.time(6, 0)
futsal.closing_time = dt.time(22, 0)
```

---

## Related Endpoints

These endpoints also depend on opening/closing times:

1. ✅ **POST /api/v1/admin/slots/generate/** - Fixed
2. ✅ **POST /api/v1/admin/slots/copy-next-day/** - Uses same service
3. ✅ **GET /api/v1/futsal/** - Returns opening/closing times

---

## Summary

✅ **Validation added** - Clear error instead of 500  
✅ **Error handling added** - Returns 400 with message  
✅ **Migration created** - Auto-fixes missing times  
✅ **Default hours set** - 6 AM to 10 PM  
✅ **Safe to deploy** - Migration is idempotent  
✅ **User-friendly errors** - Admins know what to fix  

**The slot generation endpoint is now resilient to missing configuration!** 🚀

---

## Rollback Plan

If issues occur after deployment:

1. **Revert code changes:**
```bash
git revert HEAD
git push origin main
```

2. **Or manually set times in admin panel**

3. **Migration is safe to keep** - It only helps, doesn't break anything

---

## Future Improvements

1. **Admin UI Validation:**
   - Add frontend validation in admin panel
   - Show warning if times aren't set
   - Disable slot generation button if not configured

2. **Health Check:**
   - Add health check endpoint to verify configuration
   - Include in monitoring dashboard

3. **Better Error Responses:**
   - Include link to admin panel in error message
   - Suggest specific fix steps

4. **Automated Tests:**
   - Add test for missing opening/closing times
   - Test error response format
