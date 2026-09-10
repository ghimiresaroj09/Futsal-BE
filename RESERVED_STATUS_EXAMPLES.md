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

### Request
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
