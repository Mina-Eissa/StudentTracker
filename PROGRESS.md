# StudentTracker — Progress

A tool for teachers to take attendance, log student behavior, and track
bathroom breaks per class session. Database on Supabase (Postgres), backend
on Django REST Framework, frontend in React. The frontend talks only to the
Django API — never directly to Supabase — and Django verifies
Supabase-issued JWTs on every request.

## ✅ Achieved

### Database

- Full schema designed and running in Supabase: `user`, `grade`,
  `teacher_grade`, `student`, `session`, `attendance`, `bathroom_log`,
  `behavior`, `session_student_behavior`, `event_log`.
- Row Level Security policies written for every table (kept as
  defense-in-depth — see Patterns doc for why they aren't the primary
  authorization layer in this project).
- `bathroom_log` redesigned from an aggregate row (`count_times` +
  average duration) to a true per-event log: one row per trip, with
  `started_at`, nullable `duration` (null = currently open), and `set_by`.
- `session.status` added as a real state machine (`Pending` / `Running` /
  `Finished`, backed by a `SessionStatus` TextChoices enum on the Django
  side — caught and fixed an inconsistent lowercase `'finished'` value
  during testing).
- `event_log` table added — an append-only domain event log with
  `event_type`, a polymorphic-ish reference (`session_id` or
  `teacher_grade_id` depending on the event), `triggered_by`, and a
  `metadata` JSONB column. No `UPDATE`/`DELETE` policy on it at all,
  deliberately — an event log you can edit after the fact isn't a log.
- `academic_year` table added, plus `student_grade` (new — students never
  had a grade link before) and a year dimension added to `teacher_grade`
  and `session`. Both `student_grade` and `teacher_grade` are append-only
  history, not a mutable pointer — a promotion or reassignment is a new
  row, never an overwrite.

### Backend (Django, app `core`)

- **Models** — one file per table, `managed = False`, mapped exactly onto
  the Supabase schema.
- **Auth** — `SupabaseAuthentication`, a custom DRF authentication class
  that verifies the Bearer JWT locally against Supabase's JWT secret and
  loads the matching `AppUser` as `request.user`. No network call to
  Supabase on every request.
- **Permissions** — `IsAdmin`, `IsAdminOrReadOnly`, applied per-viewset.
- **Serializers & ViewSets** — full CRUD for grades, teacher-grades,
  students, sessions, attendance, behaviors, and behavior-events, each
  scoped so a teacher only sees their own data (or everything, if Admin).
- **Auth endpoints** — `signin`, `signup`, `logout`, `me`, all proxying to
  Supabase Auth so the frontend never talks to Supabase directly.
- **Admin-gated user creation** — `POST /api/users/create/`, invite-by-email
  as the default path (no one but the invitee ever sees a password), with
  an optional admin-set-password fallback for when SMTP isn't configured.
  No open self-registration route is wired up.
- **Bathroom tracking** — separate `BathroomStartView` (by session +
  student) and `BathroomStopView` (by trip id), driven by database state
  (`duration IS NULL` *is* the "currently out" signal) rather than a
  cache — no dependency on hitting the same worker process twice.
- **Session lifecycle** — `POST /api/sessions/<id>/start/`
  (`Pending → Running`) and `POST /api/sessions/<id>/end/`
  (`→ Finished`), the latter cascading to force-close any bathroom trips
  still open for that session.
- **Observer pattern for session lifecycle events** — `signals.py`
  defines `session_set`, `session_started`, `session_ended`, and
  `grade_assigned`; `receivers.py` reacts independently (one generic
  handler persists every event to `event_log`, a separate handler closes
  open bathroom trips on `session_ended`). `EndSessionView` no longer
  imports `BathroomLog` at all — it just announces the session ended.
  Read-only `EventLogViewSet` lets a teacher (or Admin, for everything)
  browse the resulting history.
- **Reports** — per-session rollup (attendance + behavior + bathroom) and
  per-student behavior/points summary over a date range.
- **Swagger/OpenAPI docs** via drf-spectacular, ready to mount at
  `/api/docs/`.

### Testing

- Full `pytest-django` suite, one file per view/viewset, plus a shared
  `conftest.py` that bootstraps the test database's tables via raw SQL
  (necessary since every model is `managed = False`) and provides factory
  fixtures + pre-authenticated test clients (`as_admin`/`as_teacher`/
  `as_other_teacher`).
- Tests run against a disposable local Postgres, never against the real
  Supabase project.
- Real bugs caught and fixed by writing these tests, not just happy-path
  coverage:
  - `BathroomStopView` catching the wrong exception type
    (`.filter().first()` never raises `DoesNotExist`), which meant a
    missing/foreign trip 404'd via an unhandled `AttributeError` instead
    of a clean response.
  - `IsAdminOrReadOnly` incorrectly letting anonymous `GET` requests
    through, because `AnonymousUser` is truthy and the check assumed
    unauthenticated meant `request.user is None`.
  - `AppUser.objects.create()` failing without a `transaction.atomic()`
    wrapper poisoned the entire surrounding DB transaction, not just that
    one query — fixed in the admin-create-user rollback path.
  - `SessionSerializer.teacher` being required by default blocked session
    creation entirely, since `perform_create()`'s intended default never
    got a chance to run before validation failed.
  - A key-naming mismatch (`"token"` vs `"access_token"`) between
    `SignInView` and `SignUpView`'s response shapes.

### Environment / tooling issues solved

- DRF's `cc_delim_re` ImportError (Django security patch removed a symbol
  DRF's older release still imported) — fixed by upgrading `djangorestframework`.
- CORS preflight failures — middleware ordering + a trailing-slash mismatch
  between the frontend's fetch URL and Django's URL patterns.
- Where to find Supabase's anon key, service role key (legacy vs the newer
  `sb_secret_...` format), and JWT secret (legacy vs signing-keys tabs).

## 🔄 In progress / not yet wired up

- Django-side models, serializers, and views for `academic_year` and
  `student_grade` — the SQL migration is written; the Django layer to
  match it isn't built yet.
- `Session` creation doesn't yet auto-resolve which `academic_year` a new
  session belongs to from its `start_at` date.
- Final `settings.py` merge (DB connection, all the Supabase env vars,
  CORS, REST_FRAMEWORK, SPECTACULAR_SETTINGS) and mounting `core.urls` +
  the Swagger routes into the root `config/urls.py`.
- Real email delivery for the invite flow — works and is confirmed via
  logging + Supabase's Auth Logs, but no domain is verified yet, so it's
  not usable for onboarding a real teacher yet. Password fallback covers
  this gap in the meantime.
- Deployment to Render (free tier) — not started.
- React frontend — not built yet, beyond a couple of illustrative
  function rewrites (`signIn`) sketched during planning.

## 📋 Backlog / things I want to add

- Pagination + filtering (`django-filter`) on list endpoints.
- `GET /api/health/` for an external pinger, to dodge Render free-tier
  cold starts.
- Audit fields (`created_by`, `updated_at`) on the remaining log tables
  not already covered by `event_log`.
- Rate limiting on `signin`/`signup`.
- Exportable PDF/Excel reports per student or session.
- A read-only "Parent" role — deliberately deferred, not in scope yet.
