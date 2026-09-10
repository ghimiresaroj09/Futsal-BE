# Homepage — CMS Contract

`GET /api/v1/cms/homepage/` · public · cached

Covers every section of the homepage in render order:
Hero → Stats → Arena → Features → How it works → Gallery preview →
Testimonials → CTA banner.

The **live status chip** (open/closed + next free slot) is NOT part of this
response — the frontend computes it from `/futsal/` hours and
`/slots/date-wise/` for today.

## Response

```json
{
  "success": true,
  "message": "Success",
  "data": {
    "meta_title": "Nexus FMS — Book Your Futsal Slot Online",
    "meta_description": "Premium futsal courts in Kathmandu. Check live availability and book your slot online in seconds — pay at the counter.",
    "updated_at": "2026-09-08T10:12:00+05:45",

    "hero": {
      "badge": "Kathmandu's home of futsal",
      "title": "Book your slot.",
      "title_highlight": "Own the game.",
      "description": "Premium turf, floodlights and locker rooms at Nexus Futsal — reserve your hour online in seconds, gather your squad and just show up to play.",
      "image": {
        "url": "https://res.cloudinary.com/…/hero.jpg",
        "alt": "Players in a mid-match action on the Nexus Futsal court"
      },
      "primary_cta": { "label": "Book a Slot", "href": "/bookings", "style": "primary" },
      "secondary_cta": { "label": "Explore Gallery", "href": "/gallery", "style": "outline" }
    },

    "stats": [
      { "id": "courts", "value": "2", "label": "Premium courts" },
      { "id": "matches", "value": "20K+", "label": "Matches hosted" },
      { "id": "hours", "value": "6AM–10PM", "label": "Open every day" }
    ],

    "arena": {
      "eyebrow": "The Arena",
      "heading": "One arena. Built for the game.",
      "description": "Run by players, for players. Two meticulously maintained courts, quality gear and a space that's always match-ready — whether it's a casual kickabout or a cup final.",
      "since_label": "Since 2018",
      "highlights": [
        { "id": "turf", "icon": "sparkles", "text": "FIFA-quality imported turf" },
        { "id": "lights", "icon": "zap", "text": "Floodlights every evening" },
        { "id": "rooms", "icon": "shield-check", "text": "Changing rooms & hot showers" },
        { "id": "wifi", "icon": "wifi", "text": "Free Wi-Fi & spectator lounge" },
        { "id": "gear", "icon": "dumbbell", "text": "Bibs, balls & equipment provided" },
        { "id": "parking", "icon": "map-pin", "text": "Ample free parking" }
      ],
      "images": [
        { "id": "venue-indoor", "url": "https://…/venue-indoor.jpg", "alt": "Nexus Futsal's indoor court with fresh green turf" },
        { "id": "venue-rooftop", "url": "https://…/venue-rooftop.jpg", "alt": "The rooftop court at golden hour" },
        { "id": "venue-outdoor", "url": "https://…/venue-outdoor.jpg", "alt": "The outdoor pitch on game day" },
        { "id": "hero", "url": "https://…/hero.jpg", "alt": "Match night at Nexus" },
        { "id": "action-1", "url": "https://…/action-1.jpg", "alt": "Skills on display" },
        { "id": "action-2", "url": "https://…/action-2.jpg", "alt": "Post-match celebrations" }
      ]
    },

    "features": {
      "eyebrow": "Why Nexus",
      "heading": "Everything a player needs",
      "items": [
        { "id": "booking", "icon": "zap", "title": "Instant Online Booking", "description": "Reserve a court in a few taps, 24/7 — no phone calls, no waiting." },
        { "id": "availability", "icon": "clock", "title": "Live Slot Availability", "description": "Our real-time calendar shows exactly which hours are open, right now." },
        { "id": "reschedule", "icon": "calendar-clock", "title": "Free Rescheduling", "description": "Plans change? Reschedule or cancel your slot at no cost up to 12 hours before." },
        { "id": "tournaments", "icon": "trophy", "title": "Tournaments & Leagues", "description": "Join our regular leagues and knockout nights, with fixtures and standings tracked." },
        { "id": "coaching", "icon": "dumbbell", "title": "Coaching & Training", "description": "Qualified coaching sessions for kids and adults, mornings and evenings." },
        { "id": "corporate", "icon": "briefcase", "title": "Corporate & Events", "description": "Book the whole arena for corporate matches, birthdays and private events." }
      ]
    },

    "how_it_works": {
      "eyebrow": "How it works",
      "heading": "On the pitch in three steps",
      "steps": [
        { "id": "check", "icon": "clock", "title": "Check live slots", "description": "Open the booking calendar and see exactly which hours are free on each court." },
        { "id": "reserve", "icon": "calendar-check", "title": "Reserve your court", "description": "Pick your court, date and time — your slot is confirmed instantly." },
        { "id": "play", "icon": "footprints", "title": "Show up & play", "description": "Settle up at the counter when you arrive and hit the turf. It's that simple." }
      ]
    },

    "gallery_preview": {
      "eyebrow": "Gallery",
      "heading": "Straight off our turf",
      "description": "Matches, skills and celebrations from the Nexus community.",
      "count_label": "+120 photos",
      "cta": { "label": "View full gallery", "href": "/gallery", "style": "outline" },
      "photos": [
        { "id": "p1", "url": "https://…/hero.jpg", "alt": "Match night at Nexus", "aspect_ratio": "4/3" },
        { "id": "p2", "url": "https://…/action-1.jpg", "alt": "Skills on display", "aspect_ratio": "3/4" },
        { "id": "p3", "url": "https://…/venue-rooftop.jpg", "alt": "Golden hour over the court", "aspect_ratio": "1/1" },
        { "id": "p4", "url": "https://…/action-2.jpg", "alt": "Post-match celebrations", "aspect_ratio": "4/5" },
        { "id": "p5", "url": "https://…/venue-outdoor.jpg", "alt": "Game day at the arena", "aspect_ratio": "3/4" },
        { "id": "p6", "url": "https://…/venue-indoor.jpg", "alt": "Match-ready turf", "aspect_ratio": "4/3" }
      ]
    },

    "testimonials": {
      "eyebrow": "Testimonials",
      "heading": "What our players say",
      "items": [
        {
          "id": "t1",
          "quote": "Our squad books the Tuesday 8 PM slot every week. Takes 30 seconds, the turf is always in perfect shape, and the showers are a bonus.",
          "name": "Sujan Tamang",
          "role": "Captain · Kathmandu Kickers",
          "avatar": null
        },
        {
          "id": "t2",
          "quote": "We hosted our company tournament here — bookings, fixtures and the trophy ceremony all handled smoothly. The team genuinely cares.",
          "name": "Priya Shrestha",
          "role": "Organiser · Corporate League",
          "avatar": null
        },
        {
          "id": "t3",
          "quote": "I've been playing here for three years. Best-maintained court in the valley, and the coaching sessions leveled up my son's game.",
          "name": "Kamal Gurung",
          "role": "Weekly regular",
          "avatar": null
        },
        {
          "id": "t4",
          "quote": "Clean facilities, honest pricing and a booking system that actually works. This is how every futsal should be run.",
          "name": "Bibek Maharjan",
          "role": "Sunday league player",
          "avatar": null
        }
      ]
    },

    "cta_banner": {
      "heading": "Gather your squad. We'll keep the lights on.",
      "description": "Book your slot online in under a minute — or drop by the arena and see the turf for yourself.",
      "primary_cta": { "label": "Book a Slot", "href": "/bookings", "style": "secondary" },
      "secondary_cta": { "label": "Contact Us", "href": "/contact", "style": "outline" }
    }
  }
}
```

## Field notes

| Field | Type | Required | Notes |
|---|---|---|---|
| `hero.badge` | string | yes | Pill above the title. `{futsal.name}` can be interpolated server-side — the frontend also prefixes "⚽". |
| `hero.title` / `title_highlight` | string | yes | Rendered as one heading; the highlight renders in brand color. `title_highlight` may be `null`. |
| `stats[].value` | string | yes | Free-form short value ("2", "20K+", "6AM–10PM"). Exactly 3 recommended for the layout. |
| `arena.highlights[]` | array | yes | Checklist under the copy. 4–8 items. Icons optional (`icon: null` renders a checkmark). |
| `arena.images[]` | array | yes | Carousel — first image is the big frame. 4–8 recommended. |
| `arena.description` | string | yes | **Do not bake the address/name in** — the frontend appends the live location from `/futsal/`. Provide the narrative only. |
| `features.items[]` | array | yes | 6 items fit the grid best. |
| `gallery_preview.photos[]` | array | yes | Masonry collage; `aspect_ratio` drives varied tile heights. |
| `testimonials.items[].avatar` | string \| null | no | Image URL; `null` renders the person's initials. |
| `*_cta.style` | enum | no | Defaults to `primary` when omitted. |

## Rendering notes

- Section order is fixed by the page design (response sections map 1:1).
- If `testimonials.items` is empty, the whole section is hidden.
- All images lazy-loaded; carousel auto-advances every 5s (frontend behavior).
