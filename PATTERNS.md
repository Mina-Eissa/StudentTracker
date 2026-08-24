# StudentTracker — Design Patterns

Patterns actually used in this codebase, where to find them, and why they
were chosen over the alternatives that came up while building.

## Layered architecture

The `core` app is split into parallel packages by responsibility, not by
feature: `models/`, `serializers/`, `viewsets/`, `views/`. Each layer only
talks to the one below it (a viewset imports a serializer, never a raw SQL
query; a serializer imports a model, never a viewset). Every layer is
further split **one file per resource** (e.g. `models/grade.py`,
`serializers/grade.py`, `viewsets/grade.py`) rather than one flat file per
layer — keeps each file small and makes "where does X live" predictable
across all four packages at once.

## Repository-ish data access via unmanaged models

Every model has `managed = False` and an exact `db_table` mapping onto a
table Supabase's SQL Editor owns, not Django's migrations. This makes
Django's ORM act like a thin repository layer over a schema it doesn't
control the shape of — Supabase's SQL is the single source of truth for
structure; Django only describes it.

## Facade

`SignInView`, `SignUpView`, `LogoutView`, and `CreateUserView`
(`core/views/auth_*.py`, `user_management.py`) hide every direct call to
Supabase's Auth REST API behind a clean Django endpoint. The frontend never
constructs a Supabase URL or handles a Supabase-shaped error response
itself — it only ever talks to `/api/auth/...`. This is what made the later
pivot ("frontend should only talk to my backend") a real architectural
decision rather than just a preference.

## Strategy

`CreateUserView._create_with_invite` vs `_create_with_password`
(`views/user_management.py`) — two interchangeable ways to provision a new
Supabase Auth user, selected at runtime by whether the admin included a
`password` in the request. Same call site, same return contract
(`(auth_user_id, error)`), swappable without touching the rest of the view.

## Template Method

`SessionScopedViewSet` (`viewsets/base.py`) defines the shared "filter rows
down to sessions this caller owns" logic once. `AttendanceViewSet`,
`BathroomLogViewSet`, and `SessionStudentBehaviorViewSet` each just set
`queryset`/`serializer_class` and inherit the ownership-filtering behavior
— the algorithm's shape lives in one place, subclasses fill in the
specifics.

## State machine / DB-state-driven toggle

Two places encode state explicitly rather than inferring it from a client
flag:
- `bathroom_log`: a row with `duration IS NULL` **is** the "student
  currently out" signal. `BathroomLogView` (`views/bathroom.py`) checks
  for an open row and starts or stops based on what it finds — the
  database itself is the source of truth for "is this open," not a cache
  or a client-sent boolean. (This replaced an earlier version that used
  Django's cache framework to track open timers — that approach broke
  across multiple worker processes without adding Redis; moving the state
  into a real row removed that dependency entirely.)
- `session.status`: `Pending` / `Running` / `finished`, with
  `EndSessionView` (`views/session_end.py`) as the only path that moves a
  session into `finished` — and that transition cascades, force-closing
  any bathroom logs still open for that session.

## Slowly Changing Dimension (Type 2)

`student_grade` and `teacher_grade` (with `academic_year_id`) are
append-only history tables, not mutable pointers. A student's promotion or
a teacher's reassignment is a **new row**, never an `UPDATE` of an existing
`grade_id`. This is what lets "what grade was this student in during last
October's incident" stay answerable forever, and is also why
`behavior`/`session_student_behavior` points don't need an explicit
"reset" at the start of a new academic year — summaries are computed with
`Sum()` filtered by `academic_year`, so a new year naturally starts at zero
without deleting or zeroing anything.

## Custom authentication backend

`SupabaseAuthentication` (`authentication.py`) implements DRF's
`BaseAuthentication` to verify a Supabase-issued JWT locally against the
shared secret — no network round-trip to Supabase on every request. This
is the seam between "Supabase owns identity" and "Django owns
authorization" — everything downstream (`request.user`, every permission
check) depends on this class alone.

## Role-Based Access Control (RBAC)

`IsAdmin` / `IsAdminOrReadOnly` (`permissions.py`) gate write access by
`AppUser.role`. Combined with the Template Method ownership-filtering
above, this gives two independent axes of authorization: *what* a role is
allowed to do (permissions) and *which rows* they're allowed to do it to
(queryset scoping).

## Considered, not used (yet)

- **Row Level Security as the authorization layer** — every table has RLS
  policies, but Django's own database connection uses the `postgres` role
  via Supabase's connection pooler, which has `BYPASSRLS`. That means RLS
  is not what's actually protecting anything reached through the API —
  Django's permission classes and queryset scoping are. RLS is kept as
  defense-in-depth (relevant if anything ever connects to the DB a
  different way), not as the primary control.
- **Observer pattern / Django Signals for session lifecycle events** —
  discussed as a way to decouple `EndSessionView` from knowing about
  `bathroom_log` specifically (`session_ended` signal, a `receiver` in
  bathroom's own code reacting to it). Deferred in favor of a direct
  function call for now: with only one thing reacting to "session ended,"
  a signal adds indirection without a real payoff yet. Worth revisiting
  the moment a second independent reaction to session-end shows up.
