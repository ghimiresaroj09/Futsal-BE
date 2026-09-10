# Reserved Status API Response Examples

## Scenario 1: Regular User Viewing Slots with Pending Booking

### Request
```http
GET /api/v1/slots/?date=2026-09-15
Authorization: Bearer <user_token>
```

### Response
```json
{
  "success": true,
  "message": "Request successful",
  "data": {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "date": "2026-09-15",
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "price": "1000.00",
        "status": "RESERVED",  // ← Shows RESERVED because booking is PENDING
        "created_at": "2026-09-10T10:00:00Z",
        "updated_at": "2026-09-10T10:00:00Z"
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "date": "2026-09-15",
        "start_time": "11:00:00",
        "end_time": "12:00:00",
        "price": "1000.00",
        "status": "BOOKED",  // ← Shows BOOKED because booking is CONFIRMED
        "created_at": "2026-09-10T10:00:00Z",
        "updated_at": "2026-09-10T10:00:00Z"
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "date": "2026-09-15",
        "start_time": "12:00:00",
        "end_time": "13:00:00",
        "price": "1000.00",
        "status": "AVAILABLE",  // ← Shows AVAILABLE because no active booking
        "created_at": "2026-09-10T10:00:00Z",
        "updated_at": "2026-09-10T10:00:00Z"
      }
    ]
  }
}
```

## Scenario 2: Admin User Viewing Same Slots

### Request
```http
GET /api/v1/slots/?date=2026-09-15
Authorization: Bearer <admin_token>
```

### Response
```json
{
  "success": true,
  "message": "Request successful",
  "data": {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "date": "2026-09-15",
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "price": "1000.00",
        "status": "BOOKED",  // ← Admin sees actual status (BOOKED, not RESERVED)
        "created_at": "2026-09-10T10:00:00Z",
        "updated_at": "2026-09-10T10:00:00Z"
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "date": "2026-09-15",
        "start_time": "11:00:00",
        "end_time": "12:00:00",
        "price": "1000.00",
        "status": "BOOKED",  // ← Admin sees actual status
        "created_at": "2026-09-10T10:00:00Z",
        "updated_at": "2026-09-10T10:00:00Z"
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "date": "2026-09-15",
        "start_time": "12:00:00",
        "end_time": "13:00:00",
        "price": "1000.00",
        "status": "AVAILABLE",  // ← Admin sees actual status
        "created_at": "2026-09-10T10:00:00Z",
        "updated_at": "2026-09-10T10:00:00Z"
      }
    ]
  }
}
```

## Scenario 3: Anonymous User (Not Logged In)
```http
GET /api/v1/slots/?date=2026-09-15
```

### Response
```json
{
  "success": true,
  "message": "Request successful",
  "data": {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "date": "2026-09-15",
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "price": "1000.00",
        "status": "RESERVED",  // ← Anonymous users also see RESERVED
        "created_at": "2026-09-10T10:00:00Z",
        "updated_at": "2026-09-10T10:00:00Z"
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "date": "2026-09-15",
        "start_time": "11:00:00",
        "end_time": "12:00:00",
        "price": "1000.00",
        "status": "BOOKED",
        "created_at": "2026-09-10T10:00:00Z",
        "updated_at": "2026-09-10T10:00:00Z"
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "date": "2026-09-15",
        "start_time": "12:00:00",
        "end_time": "13:00:00",
        "price": "1000.00",
        "status": "AVAILABLE",
        "created_at": "2026-09-10T10:00:00Z",
        "updated_at": "2026-09-10T10:00:00Z"
      }
    ]
  }
}
```

## Status Mapping Summary

| Booking Status | Slot DB Status | User Sees | Admin Sees |
|----------------|----------------|-----------|------------|
| PENDING        | BOOKED         | RESERVED  | BOOKED     |
| CONFIRMED      | BOOKED         | BOOKED    | BOOKED     |
| COMPLETED      | BOOKED         | BOOKED    | BOOKED     |
| CANCELLED      | varies         | varies    | varies     |
| No Booking     | AVAILABLE      | AVAILABLE | AVAILABLE  |
| No Booking     | BLOCKED        | BLOCKED   | BLOCKED    |

## Use Cases

### Use Case 1: Customer Books a Slot
1. Customer books a slot at 10:00 AM
2. Booking is created with status = PENDING
3. Slot status is updated to BOOKED
4. **Other customers** browsing slots see this slot as **RESERVED** (indicating it's tentatively held)
5. **Admin** sees the slot as **BOOKED** with booking details

### Use Case 2: Admin Confirms the Booking
1. Admin reviews the booking and confirms it
2. Booking status changes from PENDING → CONFIRMED
3. Slot remains as BOOKED
4. **Other customers** now see the slot as **BOOKED** (definitively taken)
5. **Admin** continues to see BOOKED

### Use Case 3: Booking is Cancelled
1. Booking is cancelled
2. Booking status changes to CANCELLED
3. Slot status changes to AVAILABLE
4. **Everyone** sees the slot as **AVAILABLE** again

## Benefits

1. **User Experience**: Users understand that "RESERVED" slots are temporarily held pending admin confirmation
2. **Transparency**: Clear distinction between confirmed bookings (BOOKED) and pending bookings (RESERVED)
3. **Admin Control**: Admins have full visibility of actual slot statuses
4. **Data Integrity**: No changes to database schema; purely a display logic change


---

# Booking Response Examples

## Scenario 4: User Creates a Booking (Pending Status)

### Request
```http
POST /api/v1/bookings/
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "slot_id": "6cdb33d1-7fef-4184-a72f-16c63eb237ed",
  "full_name": "Saroj Ghimire",
  "email": "ghimires090@gmail.com",
  "phone_number": "9843951178",
  "notes": ""
}
```

### Response
```json
{
  "success": true,
  "message": "Booking created successfully.",
  "data": {
    "id": "2a74e656-99ca-4f30-93db-f617756d46f6",
    "booking_reference": "FSL-20260911-0004",
    "slot": {
      "id": "6cdb33d1-7fef-4184-a72f-16c63eb237ed",
      "date": "2026-09-11",
      "start_time": "08:00:00",
      "end_time": "09:00:00",
      "price": "2000.00",
      "status": "RESERVED",  // ← Shows RESERVED because booking is PENDING
      "created_at": "2026-09-10T14:52:20.660336+05:45",
      "updated_at": "2026-09-10T14:52:20.660358+05:45"
    },
    "futsal_name": "Nexus FMS Futsal",
    "full_name": "Saroj Ghimire",
    "email": "ghimires090@gmail.com",
    "phone_number": "9843951178",
    "amount": "2000.00",
    "status": "PENDING",  // ← Booking status is PENDING
    "booking_source": "USER",
    "payment_status": "PENDING",
    "payment_method": "CASH",
    "advance_amount": "0.00",
    "remaining_amount": "2000.00",
    "cancelled_at": null,
    "cancellation_reason": "",
    "notes": "",
    "created_at": "2026-09-10T15:08:51.602996+05:45",
    "updated_at": "2026-09-10T15:08:51.603015+05:45"
  }
}
```

## Scenario 5: User Views Their Pending Booking

### Request
```http
GET /api/v1/bookings/2a74e656-99ca-4f30-93db-f617756d46f6/
Authorization: Bearer <user_token>
```

### Response
```json
{
  "success": true,
  "message": "Request successful",
  "data": {
    "id": "2a74e656-99ca-4f30-93db-f617756d46f6",
    "booking_reference": "FSL-20260911-0004",
    "slot": {
      "id": "6cdb33d1-7fef-4184-a72f-16c63eb237ed",
      "date": "2026-09-11",
      "start_time": "08:00:00",
      "end_time": "09:00:00",
      "price": "2000.00",
      "status": "RESERVED",  // ← Still RESERVED for pending booking
      "created_at": "2026-09-10T14:52:20.660336+05:45",
      "updated_at": "2026-09-10T14:52:20.660358+05:45"
    },
    "futsal_name": "Nexus FMS Futsal",
    "full_name": "Saroj Ghimire",
    "email": "ghimires090@gmail.com",
    "phone_number": "9843951178",
    "amount": "2000.00",
    "status": "PENDING",
    "booking_source": "USER",
    "payment_status": "PENDING",
    "payment_method": "CASH",
    "advance_amount": "0.00",
    "remaining_amount": "2000.00",
    "cancelled_at": null,
    "cancellation_reason": "",
    "notes": "",
    "created_at": "2026-09-10T15:08:51.602996+05:45",
    "updated_at": "2026-09-10T15:08:51.603015+05:45"
  }
}
```

## Scenario 6: Admin Confirms the Booking

After admin confirms, the booking status changes to CONFIRMED.

### Request
```http
GET /api/v1/bookings/2a74e656-99ca-4f30-93db-f617756d46f6/
Authorization: Bearer <user_token>
```

### Response
```json
{
  "success": true,
  "message": "Request successful",
  "data": {
    "id": "2a74e656-99ca-4f30-93db-f617756d46f6",
    "booking_reference": "FSL-20260911-0004",
    "slot": {
      "id": "6cdb33d1-7fef-4184-a72f-16c63eb237ed",
      "date": "2026-09-11",
      "start_time": "08:00:00",
      "end_time": "09:00:00",
      "price": "2000.00",
      "status": "BOOKED",  // ← Now shows BOOKED because booking is CONFIRMED
      "created_at": "2026-09-10T14:52:20.660336+05:45",
      "updated_at": "2026-09-10T14:52:20.660358+05:45"
    },
    "futsal_name": "Nexus FMS Futsal",
    "full_name": "Saroj Ghimire",
    "email": "ghimires090@gmail.com",
    "phone_number": "9843951178",
    "amount": "2000.00",
    "status": "CONFIRMED",  // ← Booking status is now CONFIRMED
    "booking_source": "USER",
    "payment_status": "PAID",
    "payment_method": "CASH",
    "advance_amount": "0.00",
    "remaining_amount": "0.00",
    "cancelled_at": null,
    "cancellation_reason": "",
    "notes": "",
    "created_at": "2026-09-10T15:08:51.602996+05:45",
    "updated_at": "2026-09-10T15:10:22.105873+05:45"
  }
}
```

## Scenario 7: Admin Views User's Pending Booking

### Request
```http
GET /api/v1/admin/bookings/2a74e656-99ca-4f30-93db-f617756d46f6/
Authorization: Bearer <admin_token>
```

### Response
```json
{
  "success": true,
  "message": "Request successful",
  "data": {
    "id": "2a74e656-99ca-4f30-93db-f617756d46f6",
    "booking_reference": "FSL-20260911-0004",
    "slot": {
      "id": "6cdb33d1-7fef-4184-a72f-16c63eb237ed",
      "date": "2026-09-11",
      "start_time": "08:00:00",
      "end_time": "09:00:00",
      "price": "2000.00",
      "status": "RESERVED",  // ← Admin also sees RESERVED for pending bookings in booking response
      "created_at": "2026-09-10T14:52:20.660336+05:45",
      "updated_at": "2026-09-10T14:52:20.660358+05:45"
    },
    "futsal_name": "Nexus FMS Futsal",
    "full_name": "Saroj Ghimire",
    "email": "ghimires090@gmail.com",
    "phone_number": "9843951178",
    "amount": "2000.00",
    "status": "PENDING",
    "booking_source": "USER",
    "payment_status": "PENDING",
    "payment_method": "CASH",
    "advance_amount": "0.00",
    "remaining_amount": "2000.00",
    "cancelled_at": null,
    "cancellation_reason": "",
    "notes": "",
    "created_at": "2026-09-10T15:08:51.602996+05:45",
    "updated_at": "2026-09-10T15:08:51.603015+05:45"
  }
}
```

## Scenario 8: User Lists Their Bookings

### Request
```http
GET /api/v1/bookings/
Authorization: Bearer <user_token>
```

### Response
```json
{
  "success": true,
  "message": "Request successful",
  "data": {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "2a74e656-99ca-4f30-93db-f617756d46f6",
        "booking_reference": "FSL-20260911-0004",
        "slot": {
          "id": "6cdb33d1-7fef-4184-a72f-16c63eb237ed",
          "date": "2026-09-11",
          "start_time": "08:00:00",
          "end_time": "09:00:00",
          "price": "2000.00",
          "status": "RESERVED",  // ← RESERVED for pending booking
          "created_at": "2026-09-10T14:52:20.660336+05:45",
          "updated_at": "2026-09-10T14:52:20.660358+05:45"
        },
        "futsal_name": "Nexus FMS Futsal",
        "full_name": "Saroj Ghimire",
        "email": "ghimires090@gmail.com",
        "phone_number": "9843951178",
        "amount": "2000.00",
        "status": "PENDING",
        "booking_source": "USER",
        "payment_status": "PENDING",
        "payment_method": "CASH",
        "created_at": "2026-09-10T15:08:51.602996+05:45",
        "updated_at": "2026-09-10T15:08:51.603015+05:45"
      },
      {
        "id": "1a84d556-88ba-4e20-82cb-e607655d35e5",
        "booking_reference": "FSL-20260910-0003",
        "slot": {
          "id": "5cdb22c0-6dfe-3074-61ef-05c52da126dc",
          "date": "2026-09-12",
          "start_time": "10:00:00",
          "end_time": "11:00:00",
          "price": "2000.00",
          "status": "BOOKED",  // ← BOOKED for confirmed booking
          "created_at": "2026-09-09T14:52:20.660336+05:45",
          "updated_at": "2026-09-09T14:52:20.660358+05:45"
        },
        "futsal_name": "Nexus FMS Futsal",
        "full_name": "Saroj Ghimire",
        "email": "ghimires090@gmail.com",
        "phone_number": "9843951178",
        "amount": "2000.00",
        "status": "CONFIRMED",
        "booking_source": "USER",
        "payment_status": "PAID",
        "payment_method": "ESEWA",
        "created_at": "2026-09-09T14:08:51.602996+05:45",
        "updated_at": "2026-09-09T14:10:22.105873+05:45"
      }
    ]
  }
}
```

---

## Updated Status Mapping Summary

### In Slot Listing API (`/api/v1/slots/`)

| Booking Status | Slot DB Status | User Sees | Admin Sees |
|----------------|----------------|-----------|------------|
| PENDING        | BOOKED         | RESERVED  | BOOKED     |
| CONFIRMED      | BOOKED         | BOOKED    | BOOKED     |
| COMPLETED      | BOOKED         | BOOKED    | BOOKED     |
| CANCELLED      | varies         | varies    | varies     |
| No Booking     | AVAILABLE      | AVAILABLE | AVAILABLE  |
| No Booking     | BLOCKED        | BLOCKED   | BLOCKED    |

### In Booking Response API (`/api/v1/bookings/`)

| Booking Status | Slot DB Status | Everyone Sees (Users & Admins) |
|----------------|----------------|--------------------------------|
| PENDING        | BOOKED         | RESERVED                       |
| CONFIRMED      | BOOKED         | BOOKED                         |
| COMPLETED      | BOOKED         | BOOKED                         |
| CANCELLED      | AVAILABLE      | AVAILABLE                      |
| RESCHEDULED    | varies         | varies                         |

## Key Differences

### Slot Listing vs Booking Response

1. **Slot Listing (`/api/v1/slots/`)**:
   - Admins see actual slot status
   - Users/Anonymous see "RESERVED" for pending bookings
   - Purpose: Help admins manage the system while showing users what's available

2. **Booking Response (`/api/v1/bookings/`)**:
   - Everyone (including admins) sees "RESERVED" for pending bookings
   - Purpose: Consistent user experience when viewing booking details
   - The booking status field shows whether it's PENDING, CONFIRMED, etc.

This design ensures:
- Users understand their booking is pending confirmation when they see "RESERVED"
- Admins can see the full system state when managing slots
- Booking responses are consistent for everyone
