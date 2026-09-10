# Gallery Page — CMS Contract

`GET /api/v1/cms/gallery/` · public · cached

Covers the page header, category filters, the photo masonry, the video
clips section, and the closing CTA.

## Response

```json
{
  "success": true,
  "message": "Success",
  "data": {
    "meta_title": "Gallery — Nexus FMS",
    "meta_description": "Photos and clips from the Nexus Futsal community — match nights, coaching mornings and the turf itself.",
    "updated_at": "2026-09-08T10:12:00+05:45",

    "header": {
      "eyebrow": "Gallery",
      "title": "The arena, up close",
      "description": "Match nights, coaching mornings and the turf itself — a little eye candy from around Nexus. It looks even better in person."
    },

    "categories": [
      { "id": "all", "key": "ALL", "label": "All" },
      { "id": "venue", "key": "VENUE", "label": "Our Venue" },
      { "id": "matches", "key": "MATCHES", "label": "Match Nights" },
      { "id": "community", "key": "COMMUNITY", "label": "Community" }
    ],

    "photos": [
      { "id": "hero", "url": "https://…/hero.jpg", "alt": "Kickoff under the lights", "title": "Kickoff under the lights", "category": "MATCHES", "aspect_ratio": "16/10" },
      { "id": "venue-indoor", "url": "https://…/venue-indoor.jpg", "alt": "The indoor court", "title": "The indoor court", "category": "VENUE", "aspect_ratio": "3/4" },
      { "id": "action-2", "url": "https://…/action-2.jpg", "alt": "Midfield battle", "title": "Midfield battle", "category": "MATCHES", "aspect_ratio": "1/1" },
      { "id": "floodlights", "url": "https://…/floodlights.jpg", "alt": "Floodlights on", "title": "Floodlights on", "category": "VENUE", "aspect_ratio": "4/5" },
      { "id": "celebration", "url": "https://…/celebration.jpg", "alt": "That goal feeling", "title": "That goal feeling", "category": "COMMUNITY", "aspect_ratio": "4/3" },
      { "id": "venue-outdoor", "url": "https://…/venue-outdoor.jpg", "alt": "The outdoor court", "title": "The outdoor court", "category": "VENUE", "aspect_ratio": "4/3" },
      { "id": "action-1", "url": "https://…/action-1.jpg", "alt": "Saved!", "title": "Saved!", "category": "MATCHES", "aspect_ratio": "4/3" },
      { "id": "coaching", "url": "https://…/coaching.jpg", "alt": "Saturday coaching", "title": "Saturday coaching", "category": "COMMUNITY", "aspect_ratio": "3/4" },
      { "id": "turf", "url": "https://…/turf.jpg", "alt": "Fresh turf, morning light", "title": "Fresh turf, morning light", "category": "VENUE", "aspect_ratio": "1/1" },
      { "id": "venue-rooftop", "url": "https://…/venue-rooftop.jpg", "alt": "Court with a view", "title": "Court with a view", "category": "VENUE", "aspect_ratio": "16/10" }
    ],

    "videos_section": {
      "heading": "Highlights & clips",
      "description": "Short clips from around the arena — press play.",
      "videos": [
        { "id": "v-floodlights", "url": "https://…/floodlights.mp4", "poster": "https://…/floodlights.jpg", "title": "Floodlights on at dusk", "category": "VENUE", "duration_seconds": 6 },
        { "id": "v-action", "url": "https://…/action.mp4", "poster": "https://…/action-2.jpg", "title": "Match night intensity", "category": "MATCHES", "duration_seconds": 6 },
        { "id": "v-coaching", "url": "https://…/coaching.mp4", "poster": "https://…/coaching.jpg", "title": "Little legs, big dreams", "category": "COMMUNITY", "duration_seconds": 6 }
      ]
    },

    "cta": {
      "heading": "Pictures are nice. Playing is nicer.",
      "description": "Grab a slot, bring your squad and make your own highlight reel.",
      "button": { "label": "Book a Slot", "href": "/bookings", "style": "primary" }
    }
  }
}
```

## Field notes

| Field | Type | Required | Notes |
|---|---|---|---|
| `header.*` | object | yes | Centered page header. |
| `categories[]` | array | yes | Filter chips. The first entry must be the "all" category — conventionally `key: "ALL"`, which matches every photo. |
| `categories[].key` | string | yes | Uppercase enum matched against `photos[].category` / `videos[].category`. |
| `photos[]` | array | yes | Masonry grid; array order = display order. Aspect hints drive the staggered layout. |
| `photos[].alt` / `title` | string | yes | `alt` for accessibility; `title` shows on hover scrim. They may be identical. |
| `videos_section.videos[]` | array | yes | 3–6 recommended for the grid. MP4/H.264, poster required (shown before play). Keep clips small (< 5 MB) or stream via HLS. |
| `videos[].duration_seconds` | integer | yes | Rendered as an `m:ss` badge on the card. |
| `cta.*` | object | yes | Closing block under the grid. |

## Rendering notes

- Category filtering happens client-side (`category === key`, or show all
  for `"ALL"`); a photo whose category has no matching chip simply appears
  only under "All".
- The lightbox (prev/next, counters) and video player are frontend
  behavior — content only supplies the items.
- Videos autoplay muted-in-line? No — they open in a dialog player with
  controls (current behavior).
