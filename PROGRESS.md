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
  `behavior`, `session_student_behavior`.
- Row Level Security policies written for every table (kept as
  defense-in-depth — see Patterns doc for why they aren't the primary
  authorization layer in this project).
- `bathroom_log` redesigned from an aggregate row (`count_times` +
  average duration) to a true per-event log: one row per trip, with
  `started_at`, nullable `duration` (null = currently open), and `set_by`.
- `session.status` added (`Pending` / `Running` / `finished`) as a real
  state machine, not just a UI concept.
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
- **Bathroom tracking** — `POST /api/bathroom/log/` toggles start/stop
  based on database state (an open row with `duration IS NULL` *is* the
  "currently out" signal) — no cache, no dependency on hitting the same
  worker process twice.
- **Session lifecycle** — `POST /api/sessions/<id>/end/` marks a session
  finished and force-closes any bathroom trips still open for it.
- **Reports** — per-session rollup (attendance + behavior + bathroom) and
  per-student behavior/points summary over a date range.
- **Swagger/OpenAPI docs** via drf-spectacular, ready to mount at
  `/api/docs/`.

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
- No `POST /api/sessions/<id>/start/` — only the `finished` transition
  exists; `Pending` → `Running` has no endpoint yet.
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
- Audit fields (`created_by`, `updated_at`) on the log tables.
- Rate limiting on `signin`/`signup`.
- Automated tests (`pytest-django`) for the permission-scoping logic
  specifically — the part most likely to silently break as the schema
  evolves.
- Exportable PDF/Excel reports per student or session.
- A read-only "Parent" role — deliberately deferred, not in scope yet.
- Decide on Django Signals vs a plain service function for session
  lifecycle side effects (see Patterns doc) once there's a second thing
  that needs to react to "session ended," not just bathroom cleanup.
