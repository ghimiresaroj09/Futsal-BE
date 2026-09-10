# Reserved Status Update - Admin Slots Endpoint

## Change Summary

Updated the `/api/v1/admin/slots/` endpoint to show **"RESERVED"** status for slots with pending bookings, consistent with the public date-wise endpoint behavior.

## Date
September 10, 2026

---

## What Changed

### Before ❌
- **Public endpoints** (`/api/v1/slots/`, `/api/v1/slots/date-wise/`): Showed "RESERVED" for pending bookings
- **Admin endpoint** (`/api/v1/admin/slots/`): Showed actual slot status (BOOKED) even for pending bookings
- **Inconsistency**: Different behavior for admin vs. public

### After ✅
- **All endpoints**: Show "RESERVED" when a slot has a pending booking
- **Consistent behavior**: Admin and public endpoints behave the same
- **Clear indication**: "RESERVED" clearly indicates a booking is pending payment

---

## Technical Changes

### File: `futsal/serializers.py`

**Modified:** `SlotSerializer.get_status()` method

**Old Logic:**
```python
def get_status(self, obj):
    # Check if user is admin
    is_admin = (request.user.role == UserRole.ADMIN)
    
    # Admin users see the actual status (BOOKED)
    if is_admin:
        return obj.status
    
    # Non-admin users see RESERVED for pending bookings
    if has_pending_booking:
        return "RESERVED"
    
    return obj.status
```

**New Logic:**
```python
def get_status(self, obj):
    # ALL users (admin and public) see RESERVED for pending bookings
    if has_pending_booking:
        return "RESERVED"
    
    # Otherwise return the actual slot status
    return obj.status
```

---

## API Behavior

### Example Scenario

**Setup:**
1. Slot created: `2026-09-12 10:00-11:00` with status `BOOKED`
2. Booking created: `status = PENDING` (awaiting payment)

**Response:**

#### GET /api/v1/admin/slots/
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "id": "uuid",
        "date": "2026-09-12",
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "price": "1500.00",
        "status": "RESERVED"  // ✅ Shows RESERVED (was BOOKED before)
      }
    ]
  }
}
```

#### GET /api/v1/slots/date-wise/?date=2026-09-12
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "id": "uuid",
        "date": "2026-09-12",
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "price": "1500.00",
        "status": "RESERVED"  // ✅ Consistent behavior
      }
    ]
  }
}
```

---

## Status Values Explained

| Status | When Shown | Description |
|--------|-----------|-------------|
| **AVAILABLE** | No booking exists | Slot is open for booking |
| **RESERVED** | Booking status = PENDING | Booking awaiting payment confirmation |
| **BOOKED** | Booking status = CONFIRMED/COMPLETED | Booking confirmed and paid |
| **BLOCKED** | Manually blocked by admin | Slot unavailable (maintenance, holiday, etc.) |

---

## Benefits

### 1. Consistency ✅
- Admin and public endpoints show the same status
- No confusion about slot availability

### 2. Clear Communication 💬
- "RESERVED" clearly indicates a booking is pending
- Admin knows payment is awaiting confirmation

### 3. Better UX 🎯
- Admin can easily identify slots with pending bookings
- Reduces ambiguity in slot management

### 4. Payment Flow Clarity 💰
```
User creates booking → Slot shows "RESERVED"
        ↓
User pays via Khalti → Webhook confirms payment
        ↓
Booking status: PENDING → CONFIRMED
        ↓
Slot shows "BOOKED"
```

---

## Use Cases

### Admin Dashboard - Slot Management

**Scenario:** Admin viewing today's slots

**Before:**
```
10:00-11:00  [BOOKED]   ← Is this paid or pending?
11:00-12:00  [BOOKED]   ← Need to check booking details
12:00-13:00  [AVAILABLE]
```

**After:**
```
10:00-11:00  [RESERVED] ← Clearly pending payment
11:00-12:00  [BOOKED]   ← Confirmed and paid
12:00-13:00  [AVAILABLE]
```

### Filtering Pending Bookings

Admins can now easily identify slots needing payment follow-up:

```javascript
// Filter slots with pending bookings
const reservedSlots = allSlots.filter(slot => slot.status === 'RESERVED');

// Show count in dashboard
console.log(`${reservedSlots.length} slots awaiting payment`);
```

---

## Testing

### Tests Updated

**File:** `tests/test_reserved_status.py`

**Changed Test:**
```python
# Old test name: test_pending_booking_shows_normal_status_for_admin
# New test name: test_pending_booking_shows_reserved_for_admin

def test_pending_booking_shows_reserved_for_admin(admin_client, futsal, user):
    """Admin users should also see RESERVED status for pending bookings."""
    # ... create slot with pending booking ...
    
    response = admin_client.get(f"{PUBLIC_SLOTS}?date={target_date}")
    
    # Old assertion: assert results[0]["status"] == "BOOKED"
    # New assertion:
    assert results[0]["status"] == "RESERVED"  # ✅
```

### Test Results

```bash
✅ tests/test_reserved_status.py::test_pending_booking_shows_reserved_for_admin - PASSED
✅ tests/test_reserved_status.py::test_pending_booking_shows_reserved_for_users - PASSED
✅ tests/test_reserved_status.py::test_confirmed_booking_shows_booked_for_users - PASSED
✅ tests/test_reserved_status.py::test_available_slot_shows_available_for_users - PASSED
✅ tests/test_reserved_status.py::test_date_wise_endpoint_shows_reserved_for_pending - PASSED
✅ tests/test_reserved_status.py::test_date_wise_endpoint_shows_booked_for_confirmed - PASSED

✅ All tests passing (6/6)
```

---

## Frontend Integration

### No Changes Required! 🎉

The frontend already handles the "RESERVED" status correctly. This change only affects what the API returns.

**Example Frontend Code (already working):**
```javascript
function renderSlotStatus(slot) {
  const statusConfig = {
    'AVAILABLE': { color: 'green', text: 'Available' },
    'RESERVED': { color: 'orange', text: 'Reserved (Pending Payment)' },
    'BOOKED': { color: 'red', text: 'Booked' },
    'BLOCKED': { color: 'gray', text: 'Blocked' }
  };
  
  const config = statusConfig[slot.status];
  return `<span class="badge badge-${config.color}">${config.text}</span>`;
}
```

---

## Backwards Compatibility

### Impact: Minimal ⚠️

**Who is affected:**
- Admin users viewing `/api/v1/admin/slots/` endpoint

**What changes:**
- Slots with pending bookings now show "RESERVED" instead of "BOOKED"

**Breaking change?**
- **No** - This is a bug fix for consistency
- **Public endpoints** already behave this way
- **Frontend** already handles "RESERVED" status

---

## Rollback Plan

If needed, revert the change in `futsal/serializers.py`:

```python
def get_status(self, obj):
    """Revert to showing actual status for admins."""
    from common.enums import UserRole, BookingStatus
    
    request = self.context.get('request')
    is_admin = (
        request and 
        request.user and 
        request.user.is_authenticated and 
        request.user.role == UserRole.ADMIN
    )
    
    if is_admin:
        return obj.status  # Show actual status to admins
    
    # Show RESERVED to public
    if hasattr(obj, 'active_bookings'):
        pending_bookings = [
            booking for booking in obj.active_bookings 
            if booking.status == BookingStatus.PENDING
        ]
        if pending_bookings:
            return "RESERVED"
    
    return obj.status
```

---

## Related Endpoints

All these endpoints now show "RESERVED" consistently:

1. ✅ **GET /api/v1/slots/** - Public slot list
2. ✅ **GET /api/v1/slots/date-wise/** - Public date-wise slots
3. ✅ **GET /api/v1/admin/slots/** - Admin slot list (NEW)

---

## Summary

✅ **Consistent behavior** across all endpoints  
✅ **Clear status indication** for pending bookings  
✅ **All tests passing**  
✅ **No frontend changes required**  
✅ **Better admin UX**  

The admin slots endpoint now correctly shows "RESERVED" for slots with pending bookings, making it easier for admins to identify which bookings are awaiting payment confirmation.

**Status: Deployed and tested** ✅
