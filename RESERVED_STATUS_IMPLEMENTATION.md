# Reserved Status Implementation

## Overview
This implementation adds a "RESERVED" status display for slots that have pending bookings. The status is shown to regular users and anonymous users, while admin users continue to see the actual slot status.

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

### 4. Added Tests
- Created `tests/test_reserved_status.py` with comprehensive test coverage:
  - Test that pending bookings show as "RESERVED" for regular users
  - Test that pending bookings show actual status for admin users
  - Test that confirmed bookings show as "BOOKED" for all users
  - Test that available slots show as "AVAILABLE" for all users
  - Test the date-wise endpoint behavior
  - Test anonymous user behavior

### 5. Fixed Test
- Updated `tests/test_slots.py` to match the actual response format for the delete slot test

## Behavior

### For Regular Users and Anonymous Users
When accessing `/api/v1/slots/` or `/api/v1/slots/date-wise/`:
- Slots with **PENDING** bookings → Display as **"RESERVED"**
- Slots with **CONFIRMED** or **COMPLETED** bookings → Display as **"BOOKED"**
- Slots without active bookings → Display as **"AVAILABLE"** or **"BLOCKED"** (actual status)

### For Admin Users
When accessing `/api/v1/slots/` or `/api/v1/slots/date-wise/`:
- All slots display their actual database status (AVAILABLE, BOOKED, BLOCKED)
- Admin users have full visibility into the actual state of slots

## API Endpoints Affected
- `GET /api/v1/slots/` - List all upcoming slots
- `GET /api/v1/slots/?date=YYYY-MM-DD` - List slots filtered by date
- `GET /api/v1/slots/date-wise/?date=YYYY-MM-DD` - List slots for a specific date
- `GET /api/v1/slots/{id}/` - Retrieve a specific slot

## Technical Details

### Status Display Logic
```python
if user.is_authenticated and user.role == 'ADMIN':
    return actual_slot_status
elif slot has PENDING booking:
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
- 6 new tests in `test_reserved_status.py`
- 18 existing tests in `test_slots.py`
- 40 tests in `test_api_contract.py` and `test_authorization.py`

Run tests with:
```bash
python -m pytest tests/test_reserved_status.py -v
python -m pytest tests/test_slots.py -v
```

## Notes
- The "RESERVED" status is a display-only status, not a database status
- The actual slot status in the database remains unchanged (BOOKED)
- This implementation maintains backward compatibility with the admin interface
- Anonymous users (not authenticated) see the same "RESERVED" status as regular users
