# Reserved Status Feature - Flow Diagram

## Booking Lifecycle with Status Display

```
┌─────────────────────────────────────────────────────────────────────┐
│                         BOOKING LIFECYCLE                           │
└─────────────────────────────────────────────────────────────────────┘

Step 1: User Creates Booking
────────────────────────────
User → POST /api/v1/bookings/
       {
         "slot_id": "abc-123",
         "full_name": "John Doe",
         ...
       }

Database Changes:
• Booking created with status = PENDING
• Slot status updated to BOOKED

Response to User:
{
  "status": "PENDING",
  "slot": {
    "status": "RESERVED"  ← Shows RESERVED
  }
}


Step 2: Other Users Browse Slots
─────────────────────────────────
Regular User → GET /api/v1/slots/?date=2026-09-15
Admin User   → GET /api/v1/slots/?date=2026-09-15

┌──────────────────────┬─────────────────────────┐
│   Regular User Sees  │     Admin User Sees     │
├──────────────────────┼─────────────────────────┤
│  {                   │  {                      │
│    "status":         │    "status": "BOOKED"   │
│      "RESERVED"      │  }                      │
│  }                   │                         │
│                      │  (Actual database       │
│  (Slot is tentatively│   status shown)         │
│   held pending       │                         │
│   confirmation)      │                         │
└──────────────────────┴─────────────────────────┘


Step 3: User Checks Their Booking
──────────────────────────────────
User → GET /api/v1/bookings/{id}/

Response:
{
  "status": "PENDING",      ← Booking is pending
  "slot": {
    "status": "RESERVED"    ← Slot shows reserved
  }
}


Step 4: Admin Reviews Booking
──────────────────────────────
Admin → GET /api/v1/admin/bookings/{id}/

Response to Admin:
{
  "status": "PENDING",      ← Booking is pending
  "slot": {
    "status": "RESERVED"    ← Even admin sees RESERVED here
  }
}

Admin checks slots directly:
Admin → GET /api/v1/slots/{slot_id}/

Response to Admin:
{
  "status": "BOOKED"        ← Admin sees actual status
}


Step 5: Admin Confirms Booking
───────────────────────────────
Admin → PATCH /api/v1/admin/bookings/{id}/
        { "status": "CONFIRMED" }

Database Changes:
• Booking status updated to CONFIRMED
• Slot status remains BOOKED

Effect on All Endpoints:
┌─────────────────────┬──────────────────────────┐
│  GET /api/v1/slots/ │ GET /api/v1/bookings/{id}│
├─────────────────────┼──────────────────────────┤
│ Regular: "BOOKED"   │ User: {                  │
│ Admin:   "BOOKED"   │   status: "CONFIRMED",   │
│                     │   slot: {                │
│ (Both see BOOKED    │     status: "BOOKED"     │
│  now that it's      │   }                      │
│  confirmed)         │ }                        │
└─────────────────────┴──────────────────────────┘


Step 6: Booking Completed
──────────────────────────
[Time passes, booking slot time ends]

Cron Job → Booking status → COMPLETED
           Slot status remains BOOKED

All users see:
• Booking status: "COMPLETED"
• Slot status: "BOOKED"


Step 7: Booking Cancelled (Alternative Flow)
─────────────────────────────────────────────
User → POST /api/v1/bookings/{id}/cancel/

Database Changes:
• Booking status → CANCELLED
• Slot status → AVAILABLE

All users see:
• Booking status: "CANCELLED"
• Slot status: "AVAILABLE"
```

## Status State Machine

```
┌──────────────────────────────────────────────────────────────────┐
│                    SLOT STATUS DISPLAY LOGIC                     │
└──────────────────────────────────────────────────────────────────┘

Context: Slot Listing API (/api/v1/slots/)
──────────────────────────────────────────

                    Has PENDING Booking?
                           │
              ┌────────────┴────────────┐
              │                         │
             YES                        NO
              │                         │
              ▼                         ▼
         Is Admin?              Return Actual Status
              │                (AVAILABLE/BOOKED/BLOCKED)
      ┌───────┴───────┐
      │               │
     YES              NO
      │               │
      ▼               ▼
  Return "BOOKED"  Return "RESERVED"
  (Actual status)  (User-friendly)


Context: Booking Response API (/api/v1/bookings/)
──────────────────────────────────────────────────

              Booking Status?
                    │
       ┌────────────┼────────────┐
       │            │            │
    PENDING     CONFIRMED    CANCELLED
       │            │            │
       ▼            ▼            ▼
   "RESERVED"    "BOOKED"    "AVAILABLE"
 (For all users) (All users) (All users)
```

## Status Values Summary

```
┌────────────────────────────────────────────────────────────────┐
│              DATABASE vs DISPLAY STATUS VALUES                 │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Database Slot Status (enum):                                 │
│  • AVAILABLE    - Slot is open for booking                    │
│  • BOOKED       - Slot has an active booking                  │
│  • BLOCKED      - Slot is blocked by admin                    │
│                                                                │
│  Display Slot Status (in API responses):                      │
│  • AVAILABLE    - Slot is open for booking                    │
│  • RESERVED     - Slot tentatively held (pending booking)     │
│  • BOOKED       - Slot is confirmed                           │
│  • BLOCKED      - Slot is blocked by admin                    │
│                                                                │
│  Note: "RESERVED" only appears in API responses, not DB       │
└────────────────────────────────────────────────────────────────┘
```

## Decision Tree for Developers

```
When implementing status display in new endpoints:

START
  │
  ▼
Is this a slot listing/browsing endpoint?
  │
  ├─ YES → Use SlotSerializer with request context
  │         • Admins see actual status
  │         • Users see RESERVED for pending
  │
  └─ NO → Is this a booking detail/list endpoint?
          │
          ├─ YES → Use BookingSlotSerializer with booking context
          │         • Everyone sees RESERVED for pending
          │         • Everyone sees BOOKED for confirmed
          │
          └─ NO → Use standard SlotSerializer
                  (Shows actual database status)
```

## Key Takeaways

1. **Two Different Contexts**: Slot listing (management focus) vs Booking response (user experience focus)

2. **Admin Visibility**: Admins see actual status in slot listings but "RESERVED" in booking responses

3. **User Experience**: Users always see clear, consistent status indicating their booking state

4. **Database Integrity**: Only three statuses in DB (AVAILABLE, BOOKED, BLOCKED), "RESERVED" is computed

5. **No Breaking Changes**: Existing endpoints work as before, enhanced with clearer status display
