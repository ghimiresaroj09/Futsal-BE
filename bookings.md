# Bookings Page — CMS Contract

`GET /api/v1/cms/bookings/` · public · cached

Covers the page copy around the **live booking engine**: banner, how-it-works
steps, the rates panel, policies, and the help strip.

**NOT part of this response** (they come from their own live endpoints):

| Data | Source |
|---|---|
| Slot board (times, prices, statuses) | `GET /api/v1/slots/date-wise/?date=` |
| Calendar month grid + availability dots | computed from the slots endpoint |
| Arena hours / address / phone (banner chips, help strip) | `GET /api/v1/futsal/` |
| Booking creation | `POST /api/v1/bookings/` |

## Response

```json
{
  "success": true,
  "message": "Success",
  "data": {
    "meta_title": "Book a Slot — Nexus FMS",
    "meta_description": "Check live slot availability and book your futsal court online. Pay at the counter — free rescheduling up to 12 hours before.",
    "updated_at": "2026-09-08T10:12:00+05:45",

    "banner": {
      "eyebrow": "Bookings",
      "title": "Pick your date. Own your slot.",
      "description": "Browse the calendar for open hours, choose the slot that fits your squad and confirm in seconds — pay at the counter, reschedule free up to 12 hours before.",
      "image": {
        "url": "https://…/venue-indoor.jpg",
        "alt": "Nexus Futsal indoor court ready for a match"
      }
    },

    "steps": {
      "heading": "How booking works",
      "items": [
        { "id": "date", "title": "Pick a date", "description": "Browse the calendar — green dots mark dates with open slots." },
        { "id": "slot", "title": "Choose your slot", "description": "Select the hour that fits your squad, from morning to prime time." },
        { "id": "confirm", "title": "Confirm & pay at counter", "description": "Enter your details to lock the slot, then pay when you arrive." }
      ]
    },

    "rates": {
      "heading": "Rates",
      "description": "Floodlit evenings and weekends cost a little more — that's it. No hidden charges.",
      "weekday_label": "Weekday",
      "weekend_label": "Weekend",
      "rows": [
        { "id": "morning", "title": "Morning", "hours": "6 AM – 12 PM", "weekday_price": 1500, "weekend_price": 1800, "highlight": false },
        { "id": "afternoon", "title": "Afternoon", "hours": "12 PM – 5 PM", "weekday_price": 2000, "weekend_price": 2300, "highlight": false },
        { "id": "evening", "title": "Evening", "hours": "5 PM – 10 PM", "weekday_price": 2500, "weekend_price": 2800, "highlight": true, "highlight_label": "Floodlit" }
      ],
      "events": {
        "title": "Full arena & events",
        "description": "Tournaments · Corporate · Parties — block bookings welcome",
        "cta": { "label": "Contact us", "href": "/contact", "style": "outline" }
      },
      "refreshments_note": "Water, drinks and snacks are sold separately at the counter."
    },

    "policies": {
      "heading": "Good to know",
      "items": [
        { "id": "reschedule", "icon": "calendar-clock", "title": "Free rescheduling", "description": "Move or cancel your booking at no cost up to 12 hours before the slot." },
        { "id": "payment", "icon": "wallet", "title": "Pay at the counter", "description": "No online payment needed — settle up when you arrive at the arena." },
        { "id": "hold", "icon": "shield-check", "title": "Slots are held for you", "description": "Your booking locks the court for the full hour — nobody else can take it." },
        { "id": "arrive", "icon": "clock", "title": "Arrive 10 minutes early", "description": "Check in at the counter, grab bibs and a ball, and warm up before kickoff." }
      ]
    },

    "help_strip": {
      "heading": "Need a hand with your booking?",
      "description": "Call the arena — we're around from opening to close, every day.",
      "cta": { "label": "Contact Us", "href": "/contact", "style": "outline" }
    }
  }
}
```

## Field notes

| Field | Type | Required | Notes |
|---|---|---|---|
| `banner.*` | object | yes | Purple gradient photo banner. The three info chips under the text (hours · base price · location) are **composed from `/futsal/`**, not from this response. |
| `steps.items[]` | array | yes | 3–4 numbered steps. Rendered as a vertical journey with a dashed connector. |
| `rates.rows[].weekday_price` / `weekend_price` | integer | yes | NPR, whole numbers. Rendered as "Rs 1,500". |
| `rates.rows[].highlight` | boolean | no | Renders the row tinted + a badge (`highlight_label`). |
| `rates.events` | object | yes | The non-standard booking row beneath the matrix. |
| `rates.refreshments_note` | string | yes | Small note under the matrix. |
| `policies.items[]` | array | yes | 4 items fit the grid. |
| `help_strip.*` | object | yes | Purple strip above the footer; the **phone number itself is interpolated from `/futsal/`**, so the copy must not hardcode it. |

## ⚠️ Single source of truth — prices

Slot prices are already served per-slot by `GET /slots/date-wise/` (the
board shows live prices from there). The `rates.rows` above are the
**marketing summary** of the same pricing. Two acceptable strategies:

1. **Recommended**: generate `rates.rows` server-side from the same
   pricing engine that assigns slot prices — they can never drift.
2. **Simple**: store the matrix in the CMS and accept it is display-only.

Either way, the slot board always trusts the slots endpoint.
