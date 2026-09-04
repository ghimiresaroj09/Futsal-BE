# Futsal Management System — Backend

Production-ready REST API for managing futsal venues, date-wise slots, bookings,
payments/revenue, analytics dashboards, automated reminders and contact messages.

Built with **Django + DRF + PostgreSQL + JWT (Simple JWT) + Celery + Redis**, fully
documented with OpenAPI/Swagger and covered by a **191-test pytest suite** (including a
mandatory concurrency test proving double booking is impossible).

---

## 1. Overview

| Capability | Detail |
|---|---|
| Auth | Registration + email OTP verification, JWT login, refresh **with rotation & blacklist**, logout, change password, forgot/reset password |
| Roles | `USER`, `ADMIN` — admin APIs enforce `IsAuthenticated + IsAdmin` (403 for normal users) |
| Futsal | **Single venue** — one editable configuration row (pricing, opening hours); a second futsal can never be created |
| Slots | Admin CRUD + bulk generation, date-wise **whole-hour** slots (07:00 - 08:00), statuses `AVAILABLE / BOOKED / BLOCKED`, overlap prevention |
| Closures | Block a **whole day or date range** (holiday/maintenance) in one call; closed days reject bookings with `409` and are skipped by slot generation |
| Bookings | Atomic, `select_for_update()` + DB unique constraint → only **one active booking per slot** |
| Reschedule | Fully atomic slot swap with rollback; old slot released, new slot booked |
| Cancellation | Releases the slot and refunds the payment record |
| Revenue | Amount snapshotted at booking time, daily/weekly/monthly aggregation, date filtering |
| Dashboard | Today's overview, occupancy rate, graph-ready revenue & booking series |
| Reminders | Celery Beat sends a 1-hour-before email; duplicates blocked at DB level; manual admin trigger |
| Contact | Public submission + admin triage workflow |
| Cross-cutting | Standard response envelope, centralised error handling, pagination, filtering, search, whitelisted ordering, throttling, structured logging |

---

## 2. Architecture

```
futsal_backend/
├── config/
│   ├── settings/{base,development,test,production}.py
│   ├── urls.py            # /api/v1 routing
│   ├── celery.py          # Celery app + beat schedule
│   └── wsgi.py / asgi.py
├── common/                # enums, base models, permissions, validators,
│                          # pagination, exceptions, exception handler, utils, seed_data
├── accounts/              # User, OTP, auth services, profile
├── futsal/                # Futsal venue + Slot
├── bookings/              # Booking model, state machine, services, user/admin APIs
├── payments/              # Payment model + revenue selectors
├── notifications/         # Reminder model, email service, Celery tasks
├── dashboard/             # Analytics selectors + admin dashboard/revenue views
├── contact/               # ContactMessage
├── templates/emails/      # HTML email templates
└── tests/                 # pytest suite
```

**Layering:** views stay thin → `serializers` validate → `services` hold business logic and
transactions → `selectors` hold read queries → `permissions`/`validators`/`exceptions` are reusable.

---

## 3. Technology stack

Python 3.11+ · Django · Django REST Framework · PostgreSQL · Simple JWT · Celery ·
Redis · drf-spectacular · django-filter · pytest + pytest-django · Docker.

---

## 4. Installation (local)

```bash
git clone <repo> && cd futsal_backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit values
```

### Database

Set your Postgres credentials in `.env` (these are the defaults shipped in
`.env.example`):

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=futsal
DB_USER=postgres
DB_PASSWORD=postgres
```

`config/settings/base.py` reads these discrete `DB_*` variables. If a single
`DATABASE_URL` is set instead it takes precedence — handy for Docker, Heroku,
Railway, RDS and similar platforms that inject one.

```bash
createdb -U postgres futsal      # or: docker compose up -d postgres
python manage.py migrate
python manage.py createsuperuser
```

When Django opens a successful database connection, it writes a confirmation to
the process logs, for example:

```text
Database connection established: alias=default backend=postgresql database=futsal
```

This is emitted when the connection is first used (such as during migrations or
the first database-backed request), because Django opens database connections lazily.

### Seed development data

```bash
python manage.py seed_data --days 7
# admin@futsal.local / Admin@1234
# user1..3@futsal.local / User@1234
```

### Run the server

```bash
python manage.py runserver 0.0.0.0:8000
```

### Run Celery

```bash
celery -A config worker -l info        # worker
celery -A config beat   -l info        # scheduler (reminders every 5 minutes)
```

### Run tests

```bash
pytest                                  # uses config.settings.test (sqlite, locmem email)
pytest tests/test_concurrency.py -v     # the mandatory double-booking test
```

> The test settings use SQLite + in-memory email + eager Celery so the suite runs anywhere.
> To run tests against PostgreSQL, point `DATABASE_URL` at Postgres and use
> `pytest --ds=config.settings.development`.

---

## 5. Environment variables

See [`.env.example`](.env.example). Key entries: `SECRET_KEY`, `DEBUG`,
`DB_HOST`/`DB_PORT`/`DB_NAME`/`DB_USER`/`DB_PASSWORD` (or a single `DATABASE_URL`, which
overrides them),
`EMAIL_*`, `REDIS_URL`, `CELERY_*`, `JWT_ACCESS_TOKEN_LIFETIME` (minutes),
`JWT_REFRESH_TOKEN_LIFETIME` (days), `CORS_ALLOWED_ORIGINS`, OTP/reminder tuning and
throttle rates. **Never commit `.env`.**

### MongoDB production log storage (optional)

PostgreSQL remains the application's primary database. MongoDB is optional and
is used only as a structured log store. Set these values in the production
environment to activate it:

```env
MONGODB_LOG_URI=mongodb+srv://<user>:<password>@<cluster>/?retryWrites=true&w=majority
MONGODB_LOG_DATABASE=futsal_logs
MONGODB_LOG_COLLECTION=application_logs
MONGODB_LOG_LEVEL=INFO
LOG_ENVIRONMENT=production
```

Each record includes a UTC timestamp, severity, logger, message, source
location, host, environment, and exception details when present. The log handler
is fail-safe: if MongoDB cannot be reached, API requests continue and logs still
go to standard output. Leave `MONGODB_LOG_URI` blank to disable this integration
(the default for local development).

### Email / SMTP setup

Set real credentials in `.env` (never in `.env.example`, which is committed):

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=you@gmail.com
EMAIL_HOST_PASSWORD=your16charapppassword
DEFAULT_FROM_EMAIL=Futsal Arena <you@gmail.com>
```

For Gmail you must use a **16-character App Password** (Google Account →
Security → 2-Step Verification → App passwords), not your normal account
password. Enter it **without spaces**: Google displays it as `abcd efgh ijkl mnop`
but SMTP authentication requires `abcdefghijklmnop`.

Verify delivery at any time:

```bash
python manage.py test_email                  # sends to EMAIL_HOST_USER
python manage.py test_email you@example.com
```

The command prints the resolved backend/host/sender and fails loudly with the real
SMTP error if authentication is rejected.

> Development note: `config/settings/development.py` reads `EMAIL_BACKEND` from the
> environment, defaulting to the console backend. Set it explicitly in `.env` (as above)
> to send genuine email while developing. The test suite always uses an in-memory
> backend, so running `pytest` never sends real messages.

---

## 6. Media storage (Cloudinary)

Images and videos are stored in Cloudinary when all three `CLOUDINARY_*`
credentials are configured. Otherwise, uploads use the local `MEDIA_ROOT`, which
makes local development and the test suite work without a Cloudinary account.
Set `USE_CLOUDINARY=True` or `False` to override automatic detection.

Cloudinary uses separate image and video resource types. Uploads are therefore
validated and stored through the matching backend: images (`jpg`, `jpeg`, `png`,
`webp`, `gif`) are limited by `MAX_IMAGE_UPLOAD_MB` (default: 5 MB); videos
(`mp4`, `mov`, `avi`, `mkv`, `webm`) use `MAX_VIDEO_UPLOAD_MB` (default: 100 MB).

| Method | Endpoint | Access |
| --- | --- | --- |
| GET | `/api/v1/futsal-media/` | Public |
| GET | `/api/v1/futsal-media/{id}/` | Public |
| GET, POST | `/api/v1/admin/media/` | Admin |
| GET, PATCH, DELETE | `/api/v1/admin/media/{id}/` | Admin |
| PATCH | `/api/v1/users/me/` (`profile_image`) | Authenticated |

```bash
curl -X POST http://localhost:8000/api/v1/admin/media/ \
  -H "Authorization: Bearer $ACCESS" \
  -F media_type=IMAGE -F image=@court.png -F "caption=Main court"
```

## 7. API documentation

* Swagger UI — `/api/docs/`
* ReDoc — `/api/redoc/`
* OpenAPI schema — `/api/schema/`

Authorize in Swagger with `Bearer <access_token>`.

### Endpoint map

```
POST   /api/v1/auth/register/                     POST /api/v1/auth/verify-otp/
POST   /api/v1/auth/resend-otp/                   POST /api/v1/auth/login/
POST   /api/v1/auth/refresh/                      POST /api/v1/auth/logout/
POST   /api/v1/auth/change-password/              POST /api/v1/auth/forgot-password/
POST   /api/v1/auth/verify-forgot-password-otp/   POST /api/v1/auth/reset-password/

GET|PATCH /api/v1/users/me/

GET    /api/v1/futsal/            GET /api/v1/slots/?date=YYYY-MM-DD

GET|POST /api/v1/bookings/         GET /api/v1/bookings/{id}/
POST     /api/v1/bookings/{id}/cancel/
PATCH    /api/v1/bookings/{id}/reschedule/

POST   /api/v1/contact/

# admin-profile
GET|PATCH /api/v1/admin/profile/          POST /api/v1/admin/change-password/

# admin-futsal
GET|PATCH /api/v1/admin/futsal/

# admin-slots
CRUD      /api/v1/admin/slots/[{id}/]
POST      /api/v1/admin/slots/generate/      # bulk hourly slots for a date range
POST      /api/v1/admin/slots/block-day/     # close one whole day
POST      /api/v1/admin/slots/block-range/   # close a date range
POST      /api/v1/admin/slots/unblock-day/   # reopen a closed day
GET       /api/v1/admin/slots/closures/      # list closed days

# admin-bookings
CRUD      /api/v1/admin/bookings/[{id}/]
POST      /api/v1/admin/bookings/{id}/complete/
POST      /api/v1/admin/bookings/{id}/cancel/
PATCH     /api/v1/admin/bookings/{id}/reschedule/

# admin-revenue
GET       /api/v1/admin/revenue/[daily|weekly|monthly]/

# admin-dashboard
GET       /api/v1/admin/dashboard/  /dashboard/revenue/  /dashboard/bookings/  /dashboard/slots/

# admin-contact
GET|PATCH /api/v1/admin/contact/[{id}/]

# admin-reminders
GET       /api/v1/admin/reminders/[{id}/]
POST      /api/v1/admin/bookings/{id}/send-reminder/
```

### Admin API grouping

The admin surface is split into eight independent groups, each with its own URL prefix and
its own Swagger tag, so the docs read as separate sections rather than one flat list:

| Tag | Prefix | Purpose |
|---|---|---|
| `admin-profile` | `/admin/profile/`, `/admin/change-password/` | Admin's own account |
| `admin-futsal` | `/admin/futsal/` | Venue configuration: pricing, opening hours |
| `admin-slots` | `/admin/slots/` | Slot CRUD, bulk generation, whole-day closures |
| `admin-bookings` | `/admin/bookings/` | Bookings: create, update, cancel, reschedule, complete |
| `admin-revenue` | `/admin/revenue/` | Revenue totals and period breakdowns |
| `admin-dashboard` | `/admin/dashboard/` | Today's stats, occupancy, graph data |
| `admin-contact` | `/admin/contact/` | Contact message triage |
| `admin-reminders` | `/admin/reminders/` | Reminder history + manual send |

Routing lives in [`config/admin_urls.py`](config/admin_urls.py), one section per group.

### Response format

```json
{ "success": true,  "message": "Booking created successfully.", "data": {} }
{ "success": false, "message": "Slot is already booked.",       "errors": {} }
```

Status codes used: `200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500`.
`409 Conflict` is returned for double-booking attempts.

### Pagination / filtering / ordering

`?page=1&page_size=20` (default 20, max 100) → `count`, `next`, `previous`, `results`.
Bookings filter on `date, start_date, end_date, status, source, email, phone,
booking_reference`; search on reference/name/email/phone; ordering is whitelisted
(`created_at`, `status`, `slot__date`, `slot__start_time`, `amount`).

---

## 7. Authentication flow

```
register ──► unverified user + OTP email
   │
   └─► verify-otp (purpose=REGISTRATION) ──► account verified ──► access + refresh returned

login ──► access (15 min) + refresh (7 days)
refresh ──► NEW access + NEW refresh; the old refresh token is blacklisted (rotation)
logout ──► refresh token blacklisted; further use rejected
change-password / reset-password ──► ALL outstanding refresh tokens blacklisted

forgot-password ──► OTP email (response never reveals whether the email exists)
   └─► verify-forgot-password-otp ──► signed reset_token (15 min)
         └─► reset-password (email + reset_token + new password)
```

OTP rules: 6 digits, cryptographically random, **stored only as a SHA-256 hash**,
expires (default 10 min), single-use, max attempts, per-hour cap and resend cooldown, and
issuing a new OTP invalidates the previous one for that purpose.

---

## 8. Booking flow & concurrency

```
create_booking (transaction.atomic)
  1. SELECT ... FOR UPDATE on the slot          → serialises concurrent requests
  2. validate: not BLOCKED, AVAILABLE, not past, no active booking, no duplicate
  3. INSERT booking                              → UniqueConstraint(slot) WHERE status active
  4. slot.status = BOOKED
  5. create Payment with the amount snapshotted at booking time
  6. on_commit → confirmation email
```

Two simultaneous requests for the same slot → one `201 Created`, the other `409 Conflict`.
This is guaranteed by **both** row locking and the partial unique constraint
`uniq_active_booking_per_slot`, and is proven by `tests/test_concurrency.py`.

### Booking state machine

```
PENDING     → CONFIRMED, CANCELLED
CONFIRMED   → COMPLETED, CANCELLED, RESCHEDULED
RESCHEDULED → CONFIRMED, COMPLETED, CANCELLED
COMPLETED   → (terminal)      CANCELLED → (terminal)
```

Invalid transitions raise `422 Unprocessable Entity`. Cancelling releases the slot
(`BOOKED → AVAILABLE`) and refunds the payment record.

Rescheduling locks both the booking and the new slot, revalidates availability, moves the
booking, releases the old slot — all inside one transaction, so a failure never leaves two
slots booked for one booking.

---

## 9. Reminder architecture

```
Celery Beat (every 5 min)
   └─► notifications.dispatch_due_reminders
         ├─ find bookings starting in [60-10, 60] minutes without an automatic reminder
         ├─ create Reminder(AUTOMATIC_ONE_HOUR)  ← UniqueConstraint prevents duplicates
         └─ send HTML email → status SENT, or FAILED + error_message on delivery failure
```

Manual reminders (`POST /api/v1/admin/bookings/{id}/send-reminder/`) create a separate
`MANUAL` reminder record, are never silently swallowed, and return `502` with the error
logged if delivery fails.

---

## 10. Security

JWT auth · refresh rotation + blacklist · Argon2/PBKDF2 password hashing · strong password
validator (length, upper, lower, digit, special) · OTP hashing, expiry & rate limiting ·
login/OTP/register/contact throttling · CORS allowlist · secure headers + HSTS in
production · env-based secrets · object-level authorization (users only ever see their own
bookings) · ORM-only queries · no passwords, OTPs, tokens or credentials in responses or logs.

---

## 11. Docker

```bash
cp .env.example .env
docker compose up --build
```

Services: `web` (gunicorn, migrations on start), `postgres`, `redis`, `celery`,
`celery-beat`. API at http://localhost:8000, docs at http://localhost:8000/api/docs/.

Seed inside the container:

```bash
docker compose exec web python manage.py seed_data
docker compose exec web pytest
```

---

## 12. Single futsal & hourly slots

This deployment manages **one** futsal. `Futsal.objects.get_solo()` returns that single row
(creating a default if the table is empty), `Futsal.save()` refuses to insert a second row,
and `Slot.save()` attaches the venue automatically — so slot payloads never carry a
`futsal` field:

```json
POST /api/v1/admin/slots/
{ "date": "2026-09-10", "start_time": "07:00", "end_time": "08:00" }
```

Slots are validated to start **on the hour** and to last **exactly one hour**, giving the
07:00 - 08:00 style grid. To create a whole day (or range) at once, use the opening hours:

```bash
POST /api/v1/admin/slots/generate/
{ "start_date": "2026-09-10", "end_date": "2026-09-16" }
# → 06:00-07:00, 07:00-08:00, ... 21:00-22:00 for each date (idempotent, max 90 days)
```

The `futsal` foreign key is retained on `Slot`/`Booking` so multi-venue support remains a
non-breaking future change.

---

## 13. Closing the futsal for a whole day

Blocking a holiday is a single call, not one `PATCH` per slot:

```bash
POST /api/v1/admin/slots/block-day/
{ "date": "2026-10-02", "reason": "Dashain holiday" }

→ { "date": "2026-10-02", "reason": "Dashain holiday",
    "blocked_slots": 15, "cancelled_bookings": 0, "skipped_booked_slots": 1 }
```

What happens:

1. A `FutsalClosure` row is recorded (date + reason + who did it), so the closure is
   auditable and **`slots/generate/` will not repopulate that day**.
2. Every `AVAILABLE` slot on the date becomes `BLOCKED`.
3. Slots that already hold an **active booking are left untouched** and reported in
   `skipped_booked_slots` — existing customers are never silently dropped.
4. Booking any slot on a closed date returns **`409 Conflict`** with the reason:
   `"The futsal is closed on this date. (Dashain holiday)"`.

To close the day *including* existing bookings, opt in explicitly — each booking is
cancelled through the normal service, which refunds the payment and emails the customer:

```bash
POST /api/v1/admin/slots/block-day/
{ "date": "2026-10-02", "reason": "Ground flooded", "cancel_bookings": true }
```

Ranges and reopening:

```bash
POST /api/v1/admin/slots/block-range/  { "start_date": "2026-10-02", "end_date": "2026-10-05" }
POST /api/v1/admin/slots/unblock-day/  { "date": "2026-10-02" }   # BLOCKED → AVAILABLE
GET  /api/v1/admin/slots/closures/                                 # audit trail
```

Blocking is idempotent (re-blocking updates the reason, blocks 0 further slots) and past
dates are rejected.

---

## 14. Timezone

`TIME_ZONE=Asia/Kathmandu`, `USE_TZ=True`. All timestamps are stored as aware UTC and
converted with `common.utils.combine_local()` / `local_now()` whenever slot dates and times
are turned into datetimes — used for past-slot checks, one-hour reminders, revenue periods
and dashboard day boundaries.

---

## 15. Test suite

```
tests/test_auth.py           registration, OTP (invalid/expired/single-use/resend/rate-limit),
                             login, unverified login, refresh rotation, logout, passwords
tests/test_profile.py        profile read/update, uniqueness, email re-verification
tests/test_authorization.py  403/401 matrices, cross-user access, slot immutability
tests/test_slots.py          CRUD, overlap, past dates, filters, pagination
tests/test_single_futsal.py  solo-venue enforcement, whole-hour rules, bulk generation
tests/test_day_blocking.py   whole-day/range closure, booking rejection, refunds, reopen
tests/test_admin_grouping.py admin Swagger tag grouping, reminder history
tests/test_bookings.py       booking, conflicts, snapshots, history, cancel, complete, admin
tests/test_reschedule.py     success, unavailable/past slot, ownership, atomic rollback
tests/test_concurrency.py    MANDATORY threaded double-booking test + DB constraint test
tests/test_revenue.py        daily/weekly/monthly, filters, refunds, historical pricing
tests/test_dashboard.py      today's stats, occupancy (incl. divide-by-zero), graph data
tests/test_reminders.py      1-hour calculation, duplicate prevention, manual, failures
tests/test_contact.py        create, validation, admin retrieval and status update
tests/test_api_contract.py   envelopes, docs/schema, no stack-trace leakage, ordering, paging
```

```bash
$ pytest
191 passed
```
