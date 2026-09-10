# About Page — CMS Contract

`GET /api/v1/cms/about/` · public · cached

Covers every section in render order: Hero → Stats → Story & timeline →
Values → Community & coaching → Team → CTA banner.

## Response

```json
{
  "success": true,
  "message": "Success",
  "data": {
    "meta_title": "About Us — Nexus FMS",
    "meta_description": "Since 2018, Nexus Futsal has been Kathmandu's home of futsal. Meet the team, the story and the community behind the turf.",
    "updated_at": "2026-09-08T10:12:00+05:45",

    "hero": {
      "eyebrow": "About us",
      "title": "More than a court.",
      "title_highlight": "A community.",
      "description": "Since 2018, Nexus Futsal has been Kathmandu's home of futsal — two meticulously kept courts, floodlights that never quit, and a community that shows up every single week.",
      "image": {
        "url": "https://…/action-2.jpg",
        "alt": "Players competing in a match at Nexus Futsal"
      }
    },

    "stats": [
      { "id": "years", "value": "8+", "label": "Years in the game" },
      { "id": "matches", "value": "20K+", "label": "Matches hosted" },
      { "id": "tournaments", "value": "150+", "label": "Tournaments run" },
      { "id": "players", "value": "12K+", "label": "Players in the community" }
    ],

    "story": {
      "eyebrow": "Our story",
      "heading": "Built by players, for players",
      "description": "It started with one court, one dream and a lot of late evenings rolling turf. Eight years later we host everything from 6 AM kickabouts to cup finals under the floodlights — scroll through the moments that got us here.",
      "timeline_heading": "The journey so far",
      "timeline_hint": "Drag the cards or use the arrows — the story continues →",
      "milestones": [
        {
          "id": "2018",
          "year": "2018",
          "title": "One court, one dream",
          "description": "Nexus Futsal opens in Balaju Height with a single court and a borrowed mower.",
          "image": { "url": "https://…/venue-indoor.jpg", "alt": "The original court in 2018" }
        },
        {
          "id": "2021",
          "year": "2021",
          "title": "The second court",
          "description": "We double down — a second floodlit court, locker rooms and hot showers.",
          "image": { "url": "https://…/venue-outdoor.jpg", "alt": "The outdoor court after the expansion" }
        },
        {
          "id": "2024",
          "year": "2024",
          "title": "Leagues & coaching",
          "description": "Regular tournaments, kids coaching and corporate nights become part of the week.",
          "image": { "url": "https://…/coaching.jpg", "alt": "Kids coaching session on a weekend morning" }
        },
        {
          "id": "2026",
          "year": "2026",
          "title": "Book online, play more",
          "description": "Real-time online booking launches — your slot is confirmed in seconds.",
          "image": { "url": "https://…/hero.jpg", "alt": "Match night under the floodlights" }
        }
      ]
    },

    "values": {
      "eyebrow": "What we stand for",
      "heading": "The values on our badge",
      "items": [
        { "id": "community", "icon": "heart-handshake", "title": "Community first", "description": "We're run by players, for players — regulars, rookies and everyone between." },
        { "id": "facilities", "icon": "sparkles", "title": "Facilities without compromise", "description": "Turf groomed daily, gear that's actually good, showers that are actually hot." },
        { "id": "fair-play", "icon": "shield-check", "title": "Fair play, always", "description": "Transparent pricing, honest fixture lists and a red card for bad behaviour." },
        { "id": "pricing", "icon": "wallet", "title": "Priced for everyone", "description": "Morning rates that make before-work football a habit, not a splurge." }
      ]
    },

    "community": {
      "eyebrow": "Community",
      "heading": "The arena fills up long before kickoff",
      "description": "Futsal is a team game on and off the pitch. Our weeks are packed with leagues, coaching and nights where strangers leave as teammates.",
      "bullets": [
        "Weekly leagues for every level — from beginners to the A-division crowd",
        "Kids coaching on weekend mornings with qualified trainers",
        "Corporate tournaments and team-building nights",
        "Open scrimmage nights where solo players find a squad"
      ],
      "image": {
        "url": "https://…/coaching.jpg",
        "alt": "Coaching session with young players at Nexus Futsal"
      }
    },

    "team": {
      "eyebrow": "The team",
      "heading": "The people behind the turf",
      "description": "Say hi when you see us at the counter — we're usually around.",
      "members": [
        { "id": "saroj", "full_name": "Saroj Ghimire", "role": "Founder & Owner", "profile_image": null },
        { "id": "anisha", "full_name": "Anisha Karki", "role": "Arena Manager", "profile_image": null },
        { "id": "bikash", "full_name": "Bikash Shrestha", "role": "Head Coach", "profile_image": null },
        { "id": "rita", "full_name": "Rita Tamang", "role": "Operations", "profile_image": null }
      ]
    },

    "cta_banner": {
      "heading": "Come see the turf for yourself",
      "description": "Words only get you so far — book a slot, bring your squad and find out why players keep coming back to Balaju Height.",
      "primary_cta": { "label": "Book a Slot", "href": "/bookings", "style": "secondary" },
      "secondary_cta": { "label": "Contact Us", "href": "/contact", "style": "outline" }
    }
  }
}
```

## Field notes

| Field | Type | Required | Notes |
|---|---|---|---|
| `hero.title` / `title_highlight` | string | yes | The highlight renders in a lighter tone over the banner image. |
| `stats[]` | array | yes | Exactly 4 fit the strip layout. |
| `story.milestones[]` | array | yes | Draggable timeline cards. 3–6 recommended. Cards alternate image left/right automatically by index. |
| `story.timeline_hint` | string | no | Small helper line under the timeline. |
| `values.items[]` | array | yes | 4 items fit the grid; icons from the shared registry. |
| `community.bullets[]` | string[] | yes | Rendered with a leading icon per bullet. |
| `team.members[]` | array | yes | `profile_image` (URL or `null`) — `null` renders the person's initials in a brand-colored avatar. |
| `cta_banner` | object | yes | Purple gradient banner at the bottom of the page. |

## Rendering notes

- Section order is fixed by the design.
- Empty arrays hide their entire section gracefully.
- The timeline's drag/momentum/snap behavior is pure frontend — content
  only supplies the cards.
