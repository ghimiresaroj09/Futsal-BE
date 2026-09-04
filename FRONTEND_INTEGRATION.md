# Futsal Frontend Integration Guide

This guide is the implementation contract for a website or SPA consuming this
repository's API. It is based on the current Django routes, serializers,
permissions, validation rules, and booking services—not on assumed endpoints.

Use the live OpenAPI specification as the final machine-readable source of
truth:

- Swagger UI: `https://<api-host>/api/docs/`
- OpenAPI JSON: `https://<api-host>/api/schema/`
- Health probe: `https://<api-host>/healthz/`

## 1. Product model and frontend boundaries

This is a **single-venue** system: one futsal configuration is served from
`GET /api/v1/futsal/`. There is no venue-picker and client requests must never
send a `futsal_id` when creating slots or user bookings.

The frontend should have three guarded areas:

| Area | Audience | Main API domains |
| --- | --- | --- |
| Public site | Anyone | Venue, gallery, slots, contact, registration/login |
| Customer app | Authenticated `USER` | Profile and the customer's own bookings |
| Admin app | Authenticated `ADMIN` | Venue, gallery, slots, bookings, users, contacts, analytics and reminders |

Suggested route structure:

```text
/
├─ /about                     venue details + gallery
├─ /book                      date picker + available-slot grid
├─ /contact
├─ /login
├─ /register
├─ /verify-email
├─ /forgot-password
├─ /reset-password
├─ /account
│  ├─ /account/profile
│  ├─ /account/bookings
│  └─ /account/bookings/:bookingId
└─ /admin                     ADMIN role only
   ├─ /admin/dashboard
   ├─ /admin/venue
   ├─ /admin/media
   ├─ /admin/slots
   ├─ /admin/closures
   ├─ /admin/bookings
   ├─ /admin/users
   ├─ /admin/revenue
   ├─ /admin/reminders
   ├─ /admin/contact
   └─ /admin/profile
```

The application's timezone is **Asia/Kathmandu**. Slot `date` and `start_time`
values are local venue values, so render them as supplied. Do not convert
`"10:00:00"` by constructing a browser `Date` unless you explicitly attach the
Kathmandu timezone.

## 2. Base URL, headers, and response contract

Set a build-time public frontend environment variable. Never expose backend
secrets such as `CRON_SECRET` in the browser.

```env
# Vite example
VITE_API_BASE_URL=https://your-api.onrender.com/api/v1

# Next.js example
NEXT_PUBLIC_API_BASE_URL=https://your-api.onrender.com/api/v1
```

All API paths below are relative to `/api/v1`. JSON requests use:

```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <access-token>    # only for protected endpoints
```

Successful application responses have this envelope:

```json
{
  "success": true,
  "message": "Booking created successfully.",
  "data": {}
}
```

Errors have this envelope:

```json
{
  "success": false,
  "message": "Validation failed.",
  "errors": {
    "email": ["Enter a valid email address."]
  }
}
```

List endpoints return the same outer envelope, with pagination inside `data`:

```json
{
  "success": true,
  "message": "Success",
  "data": {
    "count": 42,
    "next": "https://.../?page=2",
    "previous": null,
    "results": []
  }
}
```

Use `page` and `page_size` (default `20`, maximum `100`). Treat `data.results`
as the list; do not assume list calls return a bare array.

### Status-code behavior to handle

| Status | Frontend behavior |
| --- | --- |
| `200` / `201` | Consume `data`, show the returned `message` if useful. |
| `400` | Render `errors` next to fields; use the top-level `message` as a form summary. |
| `401` | Attempt one refresh-token rotation; if it fails, clear session and go to login. |
| `403` | Show an access-denied page. Do not retry or expose admin navigation. |
| `404` | Show a missing-resource state. |
| `409` | Refresh slots/bookings and explain the conflict. This is expected during concurrent booking. |
| `422` | Show invalid state-transition feedback (for example, cancelling a completed booking). |
| `429` | Disable/retry after a delay; this commonly applies to login, OTP, register, and contact. |
| `500` / `502` | Show a retryable generic error; never show raw server text or stack traces. |

## 3. TypeScript transport layer

Keep browser code independent of a framework. The following example is suitable
for React, Next.js, Vue, or Angular wrappers.

```ts
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export type ApiSuccess<T> = { success: true; message: string; data: T };
export type ApiFailure = {
  success: false;
  message: string;
  errors: Record<string, string[] | string>;
};
export type ApiResult<T> = ApiSuccess<T> | ApiFailure;

export type Page<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export class ApiError extends Error {
  constructor(
    public status: number,
    public body: ApiFailure | null,
  ) {
    super(body?.message ?? "Request failed.");
  }
}

export async function api<T>(
  path: string,
  init: RequestInit = {},
  accessToken?: string | null,
): Promise<ApiSuccess<T>> {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  if (init.body && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });
  const body = (await response.json().catch(() => null)) as ApiResult<T> | null;
  if (!response.ok || !body || !body.success) {
    throw new ApiError(response.status, body && !body.success ? body : null);
  }
  return body;
}
```

For a multipart upload, pass `FormData` and **do not manually set**
`Content-Type`; the browser adds the required boundary.

### Session and token policy

The server returns `{ access, refresh, user }` after login and successful
registration verification. Access tokens last 15 minutes by default; refresh
tokens last 7 days. Refresh token rotation blacklists the old refresh token.

Recommended browser implementation:

1. Store the access token in memory (state/store).
2. Prefer a `Secure`, `HttpOnly`, `SameSite` cookie set by a small BFF/proxy for
   the refresh token. The current API returns refresh tokens in JSON and does
   not set this cookie itself.
3. If directly calling the API from a browser-only SPA, storage of a refresh
   token requires an explicit XSS-risk decision. `localStorage` is convenient
   but less safe; do not silently claim it is secure.
4. On one `401`, call `POST /auth/refresh/` with the current refresh token,
   atomically replace **both** tokens, then retry the original request once.
5. On refresh failure, clear all local session state and route to `/login`.
6. Call `POST /auth/logout/` with the refresh token before clearing state.

On application bootstrap, call `GET /users/me/` if a usable session exists.
Use `user.role` to route to `/admin` versus `/account`; server-side permission
checks remain authoritative.

## 4. Core data shapes

IDs are UUID strings. Decimal money values are returned as strings: display them
with a decimal/currency formatter rather than JavaScript floating-point math.

```ts
type Role = "USER" | "ADMIN";
type SlotStatus = "AVAILABLE" | "BOOKED" | "BLOCKED";
type BookingStatus = "PENDING" | "CONFIRMED" | "CANCELLED" | "COMPLETED" | "RESCHEDULED";
type PaymentStatus = "PENDING" | "PAID" | "FAILED" | "REFUNDED";

interface User {
  id: string; full_name: string; email: string; phone_number: string;
  profile_image: string | null; role: Role; is_verified: boolean; created_at: string;
}
interface Futsal {
  id: string; name: string; description: string; location: string; address: string;
  phone: string; email: string; price_per_slot: string; slot_duration: number;
  opening_time: string; closing_time: string; status: "ACTIVE" | "INACTIVE";
  created_at: string; updated_at: string;
}
interface Slot {
  id: string; date: string; start_time: string; end_time: string;
  price: string; status: SlotStatus; created_at: string; updated_at: string;
}
interface Booking {
  id: string; booking_reference: string; slot: Slot; futsal_name: string;
  full_name: string; email: string; phone_number: string; amount: string;
  status: BookingStatus; booking_source: "USER" | "ADMIN";
  payment_status: PaymentStatus | null; cancelled_at: string | null;
  cancellation_reason: string; notes: string; created_at: string; updated_at: string;
}
interface Media {
  id: string; media_type: "IMAGE" | "VIDEO"; url: string | null;
  caption: string; is_cover: boolean; sort_order: number; created_at: string;
}
```

## 5. Public-site API map

| Screen/use | Method and path | Auth | Request / integration notes |
| --- | --- | --- | --- |
| Venue/about | `GET /futsal/` | Public | Fetch once and cache briefly. |
| Gallery | `GET /futsal-media/?media_type=IMAGE&is_cover=true` | Public | Filters are optional; paginate results. Use `url` directly. |
| Slot grid | `GET /slots/?date=YYYY-MM-DD` | Public | Lists upcoming slots. Filter client display to `AVAILABLE`; retain other states to render unavailable tiles. |
| Exact date grid | `GET /slots/date-wise/?date=YYYY-MM-DD` | Public | `date` is required. Prefer this endpoint for the booking page. |
| Contact form | `POST /contact/` | Public | Throttled; disable repeated submit after success. |

Contact request:

```json
{
  "name": "Asha Shrestha",
  "email": "asha@example.com",
  "phone_number": "9812345678",
  "subject": "Weekend booking",
  "message": "Can we reserve a court on Saturday?"
}
```

Public slot filters are `date`, `start_date`, `end_date`, and `status`. Public
lists are ordered by `date,start_time` unless an allowed `ordering` query is
provided (`date`, `start_time`, `created_at`). Never present a `BOOKED` or
`BLOCKED` slot as an actionable booking option.

## 6. Authentication and account onboarding

### Registration and email verification

```text
Register → show “check your email” → verify 6-digit OTP → save tokens → /account
```

| Step | Endpoint | Body |
| --- | --- | --- |
| Register | `POST /auth/register/` | `full_name`, `email`, `phone_number`, `password`, `confirm_password` |
| Verify registration OTP | `POST /auth/verify-otp/` | `email`, `otp`, `purpose: "REGISTRATION"` |
| Resend OTP | `POST /auth/resend-otp/` | `email`, `purpose: "REGISTRATION"` |
| Login | `POST /auth/login/` | `email`, `password` |
| Refresh | `POST /auth/refresh/` | `refresh` |
| Logout | `POST /auth/logout/` | `refresh`; bearer auth required |

```json
POST /auth/register/
{
  "full_name": "Asha Shrestha",
  "email": "asha@example.com",
  "phone_number": "9812345678",
  "password": "StrongPass@123",
  "confirm_password": "StrongPass@123"
}
```

Password UI must require at least 8 characters with uppercase, lowercase,
number, and special character. Phone values must be 7–15 digits with an optional
leading `+`. Names must start with a letter and use only letters, spaces,
apostrophes, periods, or hyphens.

### Password recovery

```text
email → forgot-password → email OTP → verify-forgot-password-otp
      → reset_token → reset-password → login
```

| Endpoint | Body |
| --- | --- |
| `POST /auth/forgot-password/` | `{ "email": "..." }` |
| `POST /auth/verify-forgot-password-otp/` | `{ "email": "...", "otp": "123456" }` |
| `POST /auth/reset-password/` | `email`, `reset_token`, `new_password`, `confirm_password` |

Keep `reset_token` transient—in route state or memory—not in an analytics URL.

### Profile

| Operation | Endpoint | Body |
| --- | --- | --- |
| View profile | `GET /users/me/` | None |
| Update profile | `PATCH /users/me/` | Any of `full_name`, `email`, `phone_number`, `profile_image` |
| Change password | `POST /auth/change-password/` | `old_password`, `new_password`, `confirm_password` |

`profile_image` requires multipart form data. If an email is changed, the user
becomes unverified; direct the customer through the registration OTP verification
screen again before assuming account actions will work.

## 7. Customer booking experience

### Recommended UI flow

```text
Venue page → Book page → choose date → GET date-wise slots
→ choose AVAILABLE slot → login/register if needed → booking details
→ POST booking → confirmation screen + My Bookings
```

1. Load `GET /futsal/` to display hours and the displayed price.
2. Require the user to choose a non-past local date.
3. Fetch `/slots/date-wise/?date=<date>` whenever the date changes. Refresh it
   after a booking conflict or shortly before submitting.
4. Permit selection only where `slot.status === "AVAILABLE"`.
5. Require authentication immediately before submit (or before slot selection,
   depending on your conversion design).
6. Submit the slot UUID—not the date/time—to the booking endpoint.
7. Treat a `409` as normal race-condition feedback: show “This slot was just
   taken”, refetch the date, and require selection again.

Create a customer booking:

```http
POST /api/v1/bookings/
Authorization: Bearer <access>
Content-Type: application/json
```

```json
{
  "slot_id": "6d5dc05d-116b-4618-a141-3ed0759fca87",
  "full_name": "Asha Shrestha",
  "email": "asha@example.com",
  "phone_number": "9812345678",
  "notes": "Please call if the gate is closed."
}
```

### Customer booking endpoints

| Operation | Method/path | Body |
| --- | --- | --- |
| List own bookings | `GET /bookings/` | Query filters below |
| Booking detail | `GET /bookings/:id/` | — |
| Create | `POST /bookings/` | `slot_id`, contact snapshot, optional `notes` |
| Edit contact/notes | `PATCH /bookings/:id/` | Any of `full_name`, `email`, `phone_number`, `notes` |
| Reschedule | `PATCH /bookings/:id/reschedule/` | `{ "new_slot_id": "<uuid>" }` |
| Cancel | `POST /bookings/:id/cancel/` | `{ "reason": "Optional reason" }` |

Only the authenticated owner can access these resources. A customer booking is
created `CONFIRMED` with a `PENDING` cash payment record. Cancellation releases
the slot and refunds the associated payment record. A reschedule is atomic,
changes the status to `RESCHEDULED`, reserves the new slot, and releases the old
one.

Booking list query parameters:

```text
?date=2026-09-10
?start_date=2026-09-01&end_date=2026-09-30
?status=CONFIRMED
?search=FSL-20260910
?ordering=-created_at
?page=1&page_size=20
```

Booking ordering is limited to `created_at`, `status`, `slot__date`, and
`slot__start_time` (admin also permits `amount`). Do not expose cancellation or
rescheduling controls for `CANCELLED`/`COMPLETED` bookings. If the server returns
`422`, refresh the booking and show its current state.

### Important payment gap

The current backend does **not** expose a public payment-intent, eSewa/Khalti
initiation, payment verification, webhook, or customer payment-update endpoint.
Do not build a frontend that claims online payment is complete from this API.

For the current API, present the booking as a reservation with the returned
`payment_status` (typically `PENDING`) and payment instructions. An online
payment flow needs a backend extension before release; clients must never change
payment status themselves.

## 8. Admin application

All routes in this section require `Authorization: Bearer <admin access token>`
and `user.role === "ADMIN"`. Hide the admin shell until `GET /users/me/`
confirms that role, but rely on the API's `403` check as well.

### Admin navigation to API mapping

| Admin page | APIs |
| --- | --- |
| Dashboard | `GET /admin/dashboard/`, plus graph endpoints |
| Venue settings | `GET/PATCH /admin/futsal/` |
| Gallery | `GET/POST /admin/media/`, `GET/PATCH/DELETE /admin/media/:id/` |
| Slots | `GET/POST /admin/slots/`, `GET/PATCH/DELETE /admin/slots/:id/`; actions below |
| Closures | `GET /admin/slots/closures/`, block/unblock actions |
| Bookings | `GET/POST /admin/bookings/`, details and actions |
| Customers | `GET /admin/users/` |
| Revenue | `GET /admin/revenue/`, daily/weekly/monthly views |
| Reminders | `GET /admin/reminders/`, booking reminder action |
| Contact triage | `GET/PATCH /admin/contact/:id/` |
| My admin profile | `GET/PATCH /admin/profile/`, `POST /admin/change-password/` |

### Venue and gallery

`PATCH /admin/futsal/` accepts fields from the `Futsal` shape: `name`,
`description`, `location`, `address`, `phone`, `email`, `price_per_slot`,
`opening_time`, `closing_time`, and `status`. Opening time must be before closing
time. `slot_duration` is represented but the slot system validates one-hour
slots, so do not offer arbitrary durations in UI.

Media upload uses multipart:

```ts
const form = new FormData();
form.set("media_type", "IMAGE"); // IMAGE or VIDEO
form.set("image", selectedFile);  // use `video` for VIDEO
form.set("caption", "Main court");
form.set("is_cover", "true");
form.set("sort_order", "0");
await api<Media>("/admin/media/", { method: "POST", body: form }, accessToken);
```

Allowed image formats are `jpg`, `jpeg`, `png`, `webp`, `gif` (default max 5 MB).
Video formats are `mp4`, `mov`, `avi`, `mkv`, `webm` (default max 100 MB). Send
one matching file only. When changing an existing item's `media_type`, upload a
matching replacement file in the same request.

### Slot operations

Slots are exactly one hour and must begin/end on the hour. Common payloads:

```json
POST /admin/slots/
{ "date": "2026-10-01", "start_time": "18:00", "end_time": "19:00", "price": "1500.00", "status": "AVAILABLE" }
```

```json
POST /admin/slots/generate/
{ "start_date": "2026-10-01", "end_date": "2026-10-07" }
```

```json
POST /admin/slots/copy-next-day/
{ "date": "2026-10-02" }
```

```json
PATCH /admin/slots/bulk-update/
{ "date": "2026-10-01", "status": "BLOCKED" }
```

For per-slot changes, send `slots` instead of a date-wide status/price:

```json
{
  "date": "2026-10-01",
  "slots": [
    { "start_time": "18:00", "end_time": "19:00", "price": "1800.00" },
    { "start_time": "19:00", "end_time": "20:00", "status": "BLOCKED" }
  ]
}
```

Closing a day is preferable to PATCHing its slots individually:

```json
POST /admin/slots/block-day/
{ "date": "2026-10-02", "reason": "Maintenance", "cancel_bookings": false }
```

Use `POST /admin/slots/block-range/` with `start_date`, optional `end_date`,
optional `reason`, and `cancel_bookings`; reopen with
`POST /admin/slots/unblock-day/` and `{ "date": "..." }`. Blocking up to 90
days is supported. Existing active bookings are skipped unless
`cancel_bookings: true`; make that destructive choice visually explicit.

### Booking management

| Operation | Method/path | Body |
| --- | --- | --- |
| List / create | `GET/POST /admin/bookings/` | Create: user booking fields plus `payment_method` and optional `status` (`PENDING`/`CONFIRMED`) |
| Detail / update / delete | `GET/PATCH/DELETE /admin/bookings/:id/` | Update contact fields, `notes`, `status`, optional `reason` |
| Complete | `POST /admin/bookings/:id/complete/` | None |
| Cancel | `POST /admin/bookings/:id/cancel/` | Optional `reason` |
| Reschedule | `PATCH /admin/bookings/:id/reschedule/` | `new_slot_id` |
| Send manual reminder | `POST /admin/bookings/:id/send-reminder/` | None |

Completion marks a pending payment as paid. Deleting a booking is an admin
cancellation operation, not a hard delete; its response is a small success
object and not a full Booking resource. Build destructive-action confirmation
and refetch the list after a successful action.

### Dashboard, revenue, users, contacts, and reminders

All dashboard/revenue date filters use `start_date=YYYY-MM-DD` and
`end_date=YYYY-MM-DD`.

| Endpoint | Returns / usage |
| --- | --- |
| `GET /admin/dashboard/` | `today`, `slots`, and `revenue_summary` for initial dashboard. |
| `GET /admin/dashboard/revenue/?period=day|week|month` | `[{ date, revenue }]` for line/bar chart. |
| `GET /admin/dashboard/bookings/?period=day|week|month` | `[{ date, bookings, confirmed, cancelled, completed }]`. |
| `GET /admin/dashboard/slots/` | Available, booked, blocked, total, `occupancy_rate`. |
| `GET /admin/revenue/?payment_status=PAID` | Revenue summary: total, refunded, net, counts. |
| `GET /admin/revenue/daily/` | `{ summary, series }`; weekly/monthly paths are analogous. |
| `GET /admin/users/?search=...` | Paginated non-admin users. |
| `GET /admin/contact/?status=NEW&search=...` | Paginated contact messages. |
| `PATCH /admin/contact/:id/` | `{ "status": "IN_PROGRESS", "admin_notes": "..." }`. |
| `GET /admin/reminders/` | Paginated reminder audit records. |

Contact statuses are `NEW`, `IN_PROGRESS`, and `RESOLVED`. Chart monetary values
are decimal strings; parse using a decimal-aware library if calculations are
needed.

## 9. CORS, deployment, and server integration

The deployed backend must set `CORS_ALLOWED_ORIGINS` to the exact frontend
origin(s), such as:

```env
CORS_ALLOWED_ORIGINS=https://app.example.com,https://www.example.com
CSRF_TRUSTED_ORIGINS=https://app.example.com,https://www.example.com
```

For a direct JWT API integration, the frontend normally does not need Django
CSRF handling because it uses the `Authorization` header, not Django session
authentication. `CSRF_TRUSTED_ORIGINS` remains needed for Django admin or a
cookie/BFF architecture. Production frontend code must only use HTTPS.

Do not call either endpoint from the website:

- `GET /healthz/` is a public operational probe and may be used by uptime
  monitoring, not regular UI screens.
- `GET/POST /api/v1/internal/cron/reminders/` requires the private cron secret
  and is only for cron-job.org/secure server automation.

## 10. Launch checklist for the frontend team

- [ ] Configure a single `API_BASE_URL` with no trailing slash.
- [ ] Add the production frontend origin to backend `CORS_ALLOWED_ORIGINS`.
- [ ] Implement envelope parsing, field-error rendering, pagination, and one-time `401` refresh.
- [ ] Implement role guards and server-validated admin navigation.
- [ ] Render date/time in `Asia/Kathmandu` and money from decimal strings.
- [ ] Make booking submit idempotent in the UI (disable button while pending), while still handling backend `409` conflicts.
- [ ] Use `FormData` for profile/media files and show size/type validation errors.
- [ ] Do not expose `CRON_SECRET`, database, SMTP, Cloudinary secret, or JWT signing key in browser variables.
- [ ] Present online payments only after adding a secure backend payment initiation + verification/webhook workflow.
- [ ] Test public, user, and admin accounts against Swagger and the deployed API before launch.

## 11. Known backend constraints to preserve in UX

- A user cannot read or alter another user's booking; show only `/bookings/` results.
- Past slots cannot be created or booked.
- Slot availability can change between selection and submission; `409` is a normal outcome.
- `BLOCKED` is not the same as `BOOKED`; show a separate unavailable reason where useful.
- A futsal closure wins over individual slot availability.
- Booking cancellation may refund the stored payment record; do not promise a specific external-provider refund unless that provider is integrated.
- OTP and login are throttled. Disable repeated clicks and expose a resend countdown.
- The server currently creates a default futsal if no venue configuration exists. An admin must configure venue details, price, and opening hours before public launch.
