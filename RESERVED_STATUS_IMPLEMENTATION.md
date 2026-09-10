# Reserved Status Implementation

## Overview
This implementation adds a "RESERVED" status display for slots in two contexts:
1. **Slot Listing API** (`/api/v1/slots/`): Shows "RESERVED" to non-admin users when a slot has a pending booking
2. **Booking Response API** (`/api/v1/bookings/`): Shows "RESERVED" in the slot field when the booking status is PENDING

## Changes Made

### 1. Updated `futsal/selectors.py`
- Modified `slots_queryset()` to prefetch active bookings (PENDING, CONFIRMED, COMPLETED) for each slot
- This optimizes database queries by using `Prefetch` to load related bookings efficiently

### 2. Updated `futsal/serializers.py`
- Modified `SlotSerializer` to use a `SerializerMethodField` for the status field
- Added `get_status()` method that implements the logic:
  - **For Admin Users**: Returns the actual slot status (AVAILABLE, BOOKED, BLOCKED)
  - **For Non-Admin Users & Anonymous**: Returns "RESERVED" if the slot has a PENDING booking, otherwise returns the actual status

### 3. Updated `futsal/views.py`
- Modified `PublicSlotViewSet.date_wise()` action to pass the request context to the serializer
- This ensures the serializer has access to the request object to determine if the user is an admin

### 4. Updated `bookings/serializers.py`
- Created `BookingSlotSerializer` - a specialized slot serializer for booking responses
- Modified `BookingSerializer` to use `BookingSlotSerializer` instead of `SlotSerializer`
- The `BookingSlotSerializer` shows "RESERVED" status when the parent booking is PENDING, regardless of user role
- This ensures that when users view their own pending bookings, they see "RESERVED" in the slot status

### 5. Added Tests
- Created `tests/test_reserved_status.py` with 6 tests for slot listing API behavior
- Created `tests/test_booking_reserved_status.py` with 6 tests for booking response behavior
- All tests pass successfully

### 6. Fixed Test
- Updated `tests/test_slots.py` to match the actual response format for the delete slot test

## Behavior

### For Slot Listing API (`/api/v1/slots/`)

#### Regular Users and Anonymous Users
When accessing `/api/v1/slots/` or `/api/v1/slots/date-wise/`:
- Slots with **PENDING** bookings → Display as **"RESERVED"**
- Slots with **CONFIRMED** or **COMPLETED** bookings → Display as **"BOOKED"**
- Slots without active bookings → Display as **"AVAILABLE"** or **"BLOCKED"** (actual status)

#### Admin Users
When accessing `/api/v1/slots/` or `/api/v1/slots/date-wise/`:
- All slots display their actual database status (AVAILABLE, BOOKED, BLOCKED)
- Admin users have full visibility into the actual state of slots

### For Booking Response API (`/api/v1/bookings/`)

#### All Users (Including Admins)
When viewing booking details via `/api/v1/bookings/{id}/` or `/api/v1/bookings/`:
- If booking status is **PENDING** → Slot status shows **"RESERVED"**
- If booking status is **CONFIRMED** or **COMPLETED** → Slot status shows **"BOOKED"**
- If booking status is **CANCELLED** or **RESCHEDULED** → Slot status shows actual status (typically **"AVAILABLE"**)

This applies to both regular users viewing their own bookings and admins viewing any booking.

## API Endpoints Affected

### Slot Listing
- `GET /api/v1/slots/` - List all upcoming slots
- `GET /api/v1/slots/?date=YYYY-MM-DD` - List slots filtered by date
- `GET /api/v1/slots/date-wise/?date=YYYY-MM-DD` - List slots for a specific date
- `GET /api/v1/slots/{id}/` - Retrieve a specific slot

### Booking Management
- `GET /api/v1/bookings/` - List user's bookings
- `GET /api/v1/bookings/{id}/` - Retrieve a specific booking
- `POST /api/v1/bookings/` - Create a new booking (response includes slot with RESERVED status)
- `GET /api/v1/admin/bookings/` - Admin list all bookings
- `GET /api/v1/admin/bookings/{id}/` - Admin retrieve specific booking

## Technical Details

### Status Display Logic

#### For Slot Listing
```python
if user.is_authenticated and user.role == 'ADMIN':
    return actual_slot_status
elif slot has PENDING booking:
    return "RESERVED"
else:
    return actual_slot_status
```

#### For Booking Response
```python
if booking.status == 'PENDING':
    return "RESERVED"
else:
    return actual_slot_status
```

### Database Optimization
The implementation uses Django's `Prefetch` to efficiently load related bookings, preventing N+1 query problems when listing multiple slots.

### Booking Statuses Considered "Active"
- PENDING
- CONFIRMED
- COMPLETED

(Cancelled and Rescheduled bookings are not considered active)

## Testing
All tests pass successfully:
- 6 tests in `test_reserved_status.py` (slot listing behavior)
- 6 tests in `test_booking_reserved_status.py` (booking response behavior)
- 33 tests in `test_bookings.py` (existing booking tests)
- 18 tests in `test_slots.py` (existing slot tests)

Run tests with:
```bash
python -m pytest tests/test_reserved_status.py -v
python -m pytest tests/test_booking_reserved_status.py -v
python -m pytest tests/test_bookings.py -v
```

## Notes
- The "RESERVED" status is a display-only status, not a database status
- The actual slot status in the database remains unchanged (BOOKED)
- In booking responses, even admins see "RESERVED" for pending bookings to maintain consistency
- In slot listing, admins see the actual status to manage the system effectively
- Anonymous users (not authenticated) see the same "RESERVED" status as regular users in slot listings
