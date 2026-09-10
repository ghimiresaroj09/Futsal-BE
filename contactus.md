# Contact Page — CMS Contract

`GET /api/v1/cms/contact/` · public · cached

Covers the page header, the message form (labels, placeholders, states),
the contact details card, and the booking nudge card.

**NOT part of this response:**

| Data | Source |
|---|---|
| Actual address, phone, email, opening hours | `GET /api/v1/futsal/` (single source of truth) |
| Form submission | `POST /api/v1/contact/` (`{name, email, phone_number, subject, message}` — field set is fixed by that contract) |

The CMS response below provides **presentation copy** (labels, hints,
placeholders, state messages). The details card's *values* are merged in
from the futsal record at render time.

## Response

```json
{
  "success": true,
  "message": "Success",
  "data": {
    "meta_title": "Contact Us — Nexus FMS",
    "meta_description": "Questions about bookings, events or coaching? Reach the Nexus Futsal team by phone, email or the contact form.",
    "updated_at": "2026-09-08T10:12:00+05:45",

    "header": {
      "eyebrow": "Contact Us",
      "title": "We'd love to hear from you",
      "description": "Booking questions, event plans, a compliment for the groundskeeper — drop us a message and we'll get back to you, or reach us directly."
    },

    "form": {
      "heading": "Send us a message",
      "description": "Fill in the form below — we usually reply within a couple of hours.",
      "submit_label": "Send Message",
      "submitting_label": "Sending…",
      "fields": {
        "name":       { "label": "Full name", "placeholder": "Enter your full name" },
        "email":      { "label": "Email", "placeholder": "you@example.com" },
        "phone_number": { "label": "Phone number", "placeholder": "10-digit mobile number" },
        "subject":    { "label": "Subject", "placeholder": "e.g. Corporate event on a Saturday" },
        "message":    { "label": "Message", "placeholder": "Tell us what's on your mind" }
      },
      "success": {
        "title": "Message sent!",
        "description": "Thanks {first_name} — we'll reply to {email} within a few hours during opening times."
      },
      "again_label": "Send another message"
    },

    "details": {
      "heading": "Reach us directly",
      "description": "The counter is staffed whenever the lights are on.",
      "maps_label": "Get directions",
      "items": [
        {
          "id": "visit",
          "type": "VISIT",
          "label": "Visit",
          "hint": null,
          "value_source": "futsal.address + futsal.location"
        },
        {
          "id": "call",
          "type": "CALL",
          "label": "Call",
          "hint": "Fastest way to reach us during opening hours.",
          "value_source": "futsal.phone"
        },
        {
          "id": "email",
          "type": "EMAIL",
          "label": "Email",
          "hint": "We reply within a few hours.",
          "value_source": "futsal.email"
        },
        {
          "id": "hours",
          "type": "HOURS",
          "label": "Hours",
          "hint": "Open every day of the week.",
          "value_source": "futsal.opening_time + futsal.closing_time"
        }
      ]
    },

    "booking_card": {
      "title": "Looking to book instead?",
      "description": "Skip the queue — pick your slot online and pay at the counter.",
      "cta": { "label": "Book a Slot", "href": "/bookings", "style": "primary" }
    }
  }
}
```

## Field notes

| Field | Type | Required | Notes |
|---|---|---|---|
| `header.*` | object | yes | Centered page header. |
| `form.fields` | object | yes | Keys are **fixed** (`name`, `email`, `phone_number`, `subject`, `message`) to match the `POST /api/v1/contact/` contract. Only label/placeholder copy is editable — the field set is not. |
| `form.fields.*.label` / `placeholder` | string | yes | Rendered as the input's label and placeholder. |
| `form.success.description` | string | yes | Supports the tokens `{first_name}` and `{email}` — replaced client-side with the submitter's data. |
| `form.submit_label` / `submitting_label` | string | yes | Button text in idle / in-flight states. |
| `details.items[].type` | enum | yes | `VISIT` \| `CALL` \| `EMAIL` \| `HOURS` — controls the icon + link behavior (CALL → `tel:`, EMAIL → `mailto:`, VISIT → Google Maps). |
| `details.items[].value_source` | string | yes | Documentation-only field telling implementers which futsal field feeds the value; the frontend maps it to the live `/futsal/` data. (May be dropped from the payload if you prefer — the frontend keys off `type`.) |
| `details.items[].hint` | string \| null | no | Small muted line under the value. |
| `details.maps_label` | string | yes | The Google-Maps link text (URL is built from the live address). |
| `booking_card.*` | object | yes | Soft-purple card nudging users to the booking flow. |

## Rendering notes

- Validation (email format, 10-digit 98/97/96 phone, subject 3–80,
  message 10–500 with live counter) is enforced client-side **and** by the
  backend on `POST /contact/` — the CMS does not control rules, only copy.
- Backend field errors from the submit land inline under the matching
  inputs (existing behavior).
- If `/futsal/` fails, details values fall back to sensible defaults
  rather than blank rows.
