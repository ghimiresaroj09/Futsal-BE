# Closure Response Feature - Public Slot Endpoints

## Overview

When admins block a day or date range using the admin endpoints, the public slot endpoints now return a clear closure message with the reason, making it easy for users to understand why bookings are unavailable.

## Date
September 10, 2026

---

## Feature Summary

### Before ❌
- Admin blocks a day via `/api/v1/admin/slots/block-day/`
- Public endpoints returned empty slot list `[]`
- Users confused - "Why are there no slots?"
- No information about closure reason

### After ✅
- Admin blocks a day with reason (e.g., "Public Holiday - Dashain")
- Public endpoints return structured closure information
- Users see clear message: "Facility is closed on 2026-09-13. Public Holiday - Dashain"
- Frontend can display closure notice prominently

---

## Admin Endpoints (Block/Unblock)

### 🔴 POST - Block Single Day

**Endpoint:**
```
POST /api/v1/admin/slots/block-day/
```

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "date": "2026-12-25",
  "reason": "Christmas Day - Public Holiday",
  "cancel_bookings": true
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Day blocked successfully.",
  "data": {
    "date": "2026-12-25",
    "slots_blocked": 15,
    "bookings_cancelled": 3,
    "reason": "Christmas Day - Public Holiday"
  }
}
```

---

### 🔴 POST - Block Date Range

**Endpoint:**
```
POST /api/v1/admin/slots/block-range/
```

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "start_date": "2026-10-24",
  "end_date": "2026-10-26",
  "reason": "Dashain Festival",
  "cancel_bookings": true
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Date range blocked successfully.",
  "data": {
    "days_blocked": 3,
    "total_slots_blocked": 45,
    "total_bookings_cancelled": 8,
    "results": [
      {
        "date": "2026-10-24",
        "slots_blocked": 15,
        "bookings_cancelled": 2
      },
      {
        "date": "2026-10-25",
        "slots_blocked": 15,
        "bookings_cancelled": 4
      },
      {
        "date": "2026-10-26",
        "slots_blocked": 15,
        "bookings_cancelled": 2
      }
    ]
  }
}
```

---

### 🟢 POST - Unblock Day

**Endpoint:**
```
POST /api/v1/admin/slots/unblock-day/
```

**Authentication:** Required (Admin only)

**Request Body:**
```json
{
  "date": "2026-12-25"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Day reopened successfully.",
  "data": {
    "date": "2026-12-25",
    "slots_unblocked": 15
  }
}
```

---

## Public Endpoints (Closure Response)

### 🔵 GET - Date-Wise Slots (Closed Date)

**Endpoint:**
```
GET /api/v1/slots/date-wise/?date=2026-12-25
```

**Authentication:** None (Public)

**Scenario:** Date is blocked by admin

**Response:**
```json
{
  "status": "success",
  "message": "Facility is closed on 2026-12-25. Christmas Day - Public Holiday",
  "data": {
    "date": "2026-12-25",
    "is_closed": true,
    "reason": "Christmas Day - Public Holiday",
    "slots": []
  }
}
```

**Response (No Reason Provided):**
```json
{
  "status": "success",
  "message": "Facility is closed on 2026-12-25. No bookings available.",
  "data": {
    "date": "2026-12-25",
    "is_closed": true,
    "reason": "Facility closed",
    "slots": []
  }
}
```

---

### 🔵 GET - Date-Wise Slots (Open Date)

**Endpoint:**
```
GET /api/v1/slots/date-wise/?date=2026-09-15
```

**Authentication:** None (Public)

**Scenario:** Date is open for bookings

**Response:**
```json
{
  "status": "success",
  "message": "Slots retrieved successfully.",
  "data": {
    "count": 15,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "uuid-1",
        "date": "2026-09-15",
        "start_time": "06:00:00",
        "end_time": "07:00:00",
        "price": "1500.00",
        "status": "AVAILABLE"
      },
      {
        "id": "uuid-2",
        "date": "2026-09-15",
        "start_time": "07:00:00",
        "end_time": "08:00:00",
        "price": "1500.00",
        "status": "AVAILABLE"
      }
      // ... more slots
    ]
  }
}
```

---

### 🔵 GET - List Slots with Date Filter (Closed Date)

**Endpoint:**
```
GET /api/v1/slots/?date=2026-12-25
```

**Authentication:** None (Public)

**Scenario:** Date is blocked

**Response:**
```json
{
  "status": "success",
  "message": "Facility is closed on 2026-12-25. Christmas Day - Public Holiday",
  "data": {
    "date": "2026-12-25",
    "is_closed": true,
    "reason": "Christmas Day - Public Holiday",
    "results": []
  }
}
```

---

### 🔵 GET - List All Upcoming Slots (No Date Filter)

**Endpoint:**
```
GET /api/v1/slots/
```

**Authentication:** None (Public)

**Scenario:** No date filter - shows all upcoming slots

**Response:**
```json
{
  "status": "success",
  "message": "Slots retrieved successfully.",
  "data": {
    "count": 150,
    "next": "http://localhost:8000/api/v1/slots/?page=2",
    "previous": null,
    "results": [
      {
        "id": "uuid-1",
        "date": "2026-09-11",
        "start_time": "06:00:00",
        "end_time": "07:00:00",
        "price": "1500.00",
        "status": "AVAILABLE"
      }
      // ... more slots from multiple dates
    ]
  }
}
```

**Note:** When no date filter is provided, closure information is NOT shown. The list includes slots from all upcoming dates (excluding blocked dates automatically).

---

## Use Cases

### Use Case 1: Public Holiday Closure

**Admin Action:**
```bash
POST /api/v1/admin/slots/block-range/
{
  "start_date": "2026-10-24",
  "end_date": "2026-10-26",
  "reason": "Dashain Festival",
  "cancel_bookings": true
}
```

**User Experience:**
```bash
# User tries to book on Oct 25
GET /api/v1/slots/date-wise/?date=2026-10-25

Response:
{
  "message": "Facility is closed on 2026-10-25. Dashain Festival",
  "data": {
    "is_closed": true,
    "reason": "Dashain Festival",
    "slots": []
  }
}
```

**Frontend Display:**
```
┌────────────────────────────────────────┐
│  📅 October 25, 2026                   │
├────────────────────────────────────────┤
│                                        │
│  🚫 Facility Closed                    │
│                                        │
│  Dashain Festival                      │
│                                        │
│  We apologize for the inconvenience.   │
│  Please select another date.           │
│                                        │
└────────────────────────────────────────┘
```

---

### Use Case 2: Maintenance Work

**Admin Action:**
```bash
POST /api/v1/admin/slots/block-day/
{
  "date": "2026-09-20",
  "reason": "Facility maintenance and turf replacement",
  "cancel_bookings": false
}
```

**User Experience:**
```bash
GET /api/v1/slots/date-wise/?date=2026-09-20

Response:
{
  "message": "Facility is closed on 2026-09-20. Facility maintenance and turf replacement",
  "data": {
    "is_closed": true,
    "reason": "Facility maintenance and turf replacement"
  }
}
```

---

### Use Case 3: Emergency Closure (No Reason)

**Admin Action:**
```bash
POST /api/v1/admin/slots/block-day/
{
  "date": "2026-09-18",
  "reason": "",  # No reason provided
  "cancel_bookings": true
}
```

**User Experience:**
```bash
GET /api/v1/slots/date-wise/?date=2026-09-18

Response:
{
  "message": "Facility is closed on 2026-09-18. No bookings available.",
  "data": {
    "is_closed": true,
    "reason": "Facility closed",  # Default message
    "slots": []
  }
}
```

---

## Frontend Integration

### React Example - Date Picker with Closure Check

```jsx
import { useState, useEffect } from 'react';

function DateSlotSelector() {
  const [selectedDate, setSelectedDate] = useState(null);
  const [slots, setSlots] = useState([]);
  const [closure, setClosure] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const fetchSlots = async (date) => {
    setLoading(true);
    setClosure(null);
    setSlots([]);
    
    try {
      const response = await fetch(
        `/api/v1/slots/date-wise/?date=${date}`
      );
      const result = await response.json();
      
      // Check if date is closed
      if (result.data.is_closed) {
        setClosure({
          date: result.data.date,
          reason: result.data.reason
        });
      } else {
        setSlots(result.data.results || []);
      }
    } catch (error) {
      console.error('Failed to load slots:', error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    if (selectedDate) {
      fetchSlots(selectedDate);
    }
  }, [selectedDate]);
  
  return (
    <div className="slot-selector">
      <input
        type="date"
        value={selectedDate || ''}
        onChange={(e) => setSelectedDate(e.target.value)}
        min={new Date().toISOString().split('T')[0]}
      />
      
      {loading && <div className="loading">Loading slots...</div>}
      
      {closure && (
        <div className="closure-notice">
          <div className="icon">🚫</div>
          <h3>Facility Closed</h3>
          <p className="date">{closure.date}</p>
          <p className="reason">{closure.reason}</p>
          <p className="message">
            We apologize for the inconvenience. 
            Please select another date.
          </p>
        </div>
      )}
      
      {!closure && slots.length > 0 && (
        <div className="slots-grid">
          {slots.map(slot => (
            <div key={slot.id} className={`slot-card ${slot.status}`}>
              <span className="time">
                {slot.start_time.slice(0, 5)} - {slot.end_time.slice(0, 5)}
              </span>
              <span className="price">NPR {slot.price}</span>
              <button disabled={slot.status !== 'AVAILABLE'}>
                {slot.status === 'AVAILABLE' ? 'Book Now' : slot.status}
              </button>
            </div>
          ))}
        </div>
      )}
      
      {!closure && !loading && slots.length === 0 && (
        <div className="no-slots">
          No slots available for this date.
        </div>
      )}
    </div>
  );
}
```

---

### JavaScript Example - Calendar View

```javascript
class CalendarView {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.closedDates = new Set();
    this.closureReasons = new Map();
  }
  
  async loadClosures(startDate, endDate) {
    // Fetch all closures for the month
    const response = await fetch(
      `/api/v1/admin/slots/closures/?start_date=${startDate}&end_date=${endDate}`
    );
    const result = await response.json();
    
    result.data.forEach(closure => {
      this.closedDates.add(closure.date);
      this.closureReasons.set(closure.date, closure.reason);
    });
    
    this.render();
  }
  
  renderDay(date) {
    const dateStr = date.toISOString().split('T')[0];
    const isClosed = this.closedDates.has(dateStr);
    const reason = this.closureReasons.get(dateStr);
    
    const dayElement = document.createElement('div');
    dayElement.className = `calendar-day ${isClosed ? 'closed' : 'open'}`;
    dayElement.innerHTML = `
      <span class="date-number">${date.getDate()}</span>
      ${isClosed ? `
        <span class="closed-badge">Closed</span>
        <div class="tooltip">${reason || 'Facility closed'}</div>
      ` : ''}
    `;
    
    dayElement.addEventListener('click', () => {
      if (isClosed) {
        this.showClosureModal(dateStr, reason);
      } else {
        this.showSlots(dateStr);
      }
    });
    
    return dayElement;
  }
  
  showClosureModal(date, reason) {
    alert(`Facility is closed on ${date}\n\n${reason || 'No bookings available'}`);
  }
  
  async showSlots(date) {
    const response = await fetch(`/api/v1/slots/date-wise/?date=${date}`);
    const result = await response.json();
    
    if (result.data.is_closed) {
      this.showClosureModal(date, result.data.reason);
    } else {
      // Show slots modal/page
      this.renderSlotsModal(result.data.results);
    }
  }
}

// Usage
const calendar = new CalendarView('calendar-container');
calendar.loadClosures('2026-09-01', '2026-09-30');
```

---

## Response Structure

### Closure Response (Closed Date)

```typescript
interface ClosureResponse {
  status: 'success';
  message: string;  // e.g., "Facility is closed on 2026-12-25. Christmas Day"
  data: {
    date: string;        // ISO date format: "2026-12-25"
    is_closed: true;
    reason: string;      // Admin-provided reason or "Facility closed"
    slots?: [];          // Always empty for date-wise
    results?: [];        // Always empty for list with date filter
  };
}
```

### Normal Response (Open Date)

```typescript
interface NormalResponse {
  status: 'success';
  message: string;  // e.g., "Slots retrieved successfully."
  data: {
    count: number;
    next: string | null;
    previous: string | null;
    results: Slot[];
  };
}
```

---

## CSS Example for Closure Notice

```css
.closure-notice {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  margin: 2rem 0;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.closure-notice .icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.closure-notice h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.closure-notice .date {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 1rem;
}

.closure-notice .reason {
  font-size: 1.2rem;
  font-weight: 500;
  margin-bottom: 1rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.75rem;
  border-radius: 8px;
}

.closure-notice .message {
  font-size: 0.9rem;
  opacity: 0.8;
}

/* Calendar day styling */
.calendar-day.closed {
  background: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
  position: relative;
}

.calendar-day.closed .closed-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #dc3545;
  color: white;
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.calendar-day.closed:hover .tooltip {
  display: block;
}

.calendar-day .tooltip {
  display: none;
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #333;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  white-space: nowrap;
  font-size: 0.85rem;
  z-index: 1000;
  margin-bottom: 8px;
}

.calendar-day .tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: #333;
}
```

---

## Technical Implementation

### Files Modified

1. **futsal/views.py** - `PublicSlotViewSet`
   - Added closure check in `date_wise()` method
   - Added closure check in `list()` method override
   - Returns structured closure response when date is blocked

2. **tests/test_closure_response.py** - New test file
   - 5 comprehensive tests covering all scenarios
   - Tests closure response format
   - Tests normal slot response when date is open

### Database Query

```python
# Check if date is closed
closure = FutsalClosure.objects.covering(target_date).first()

# FutsalClosure model
class FutsalClosure(BaseModel):
    futsal = ForeignKey(Futsal)
    date = DateField()  # The blocked date
    reason = CharField()  # Why it's closed
    created_by = ForeignKey(User)  # Who blocked it
```

---

## Benefits

### 1. Clear Communication ✅
- Users immediately know why bookings are unavailable
- Reduces confusion and support queries
- Professional user experience

### 2. Better Planning 📅
- Users can see closure reasons in advance
- Can plan around holidays and maintenance
- Improves customer satisfaction

### 3. Admin Control 🎛️
- Admins can provide context for closures
- Different reasons for different dates
- Easy to manage closures

### 4. Frontend Flexibility 🎨
- Structured data for custom UI
- Easy to integrate with calendars
- Can style differently based on closure reason

---

## Testing

### Run Tests

```bash
# Run closure response tests
python -m pytest tests/test_closure_response.py -v

# Run all slot tests
python -m pytest tests/test_slots.py -v
```

### Test Results

```
✅ test_date_wise_shows_closure_message - PASSED
✅ test_list_with_date_filter_shows_closure - PASSED
✅ test_closure_without_reason_shows_default_message - PASSED
✅ test_open_date_returns_normal_slots - PASSED
✅ test_list_without_date_filter_ignores_closures - PASSED

All tests passing (5/5)
```

---

## Summary

✅ **Admin blocks date** → Public APIs show closure info  
✅ **Structured response** with date, reason, and is_closed flag  
✅ **Clear messages** in response.message field  
✅ **Default message** when no reason provided  
✅ **Normal behavior** for open dates  
✅ **Full test coverage** for all scenarios  
✅ **Easy frontend integration** with structured data  

**The public slot endpoints now provide clear closure information to users!** 🚀
