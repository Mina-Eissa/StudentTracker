import uuid

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import AppUser, Grade, Student, Behavior, Session, SessionStatus, BathroomLog

# ============================================================
# Table bootstrap — our models are managed=False (Supabase owns the real
# schema), so Django's normal migrate step creates none of these tables in
# the test database. This mirrors the same CREATE TABLE statements from the
# Supabase migrations, minus anything Postgres-in-a-test-container doesn't
# have (there's no `auth` schema here, so no FK to auth.users; RLS is
# skipped too, since it isn't the operative access-control layer anyway —
# see PATTERNS.md).
# ============================================================

TEST_SCHEMA_SQL = """
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('Teacher','Admin');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE grade_section AS ENUM ('A','B','C','D','E','F');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE attendance_status AS ENUM ('Present','Absent','Late','Excused');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE behavior_type AS ENUM ('Positive','Negative');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE session_status AS ENUM ('Pending','Running','Finished');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE event_type AS ENUM ('session_set','session_started','session_ended','grade_assigned');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS "user" (
    id          UUID          PRIMARY KEY,
    first_name  VARCHAR(100)  NOT NULL,
    middle_name VARCHAR(100),
    last_name   VARCHAR(100)  NOT NULL,
    email       VARCHAR(256)  NOT NULL UNIQUE,
    role        user_role     NOT NULL,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS grade (
    id          UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    level       INT           NOT NULL,
    section     grade_section NOT NULL,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS teacher_grade (
    id          UUID       PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id  UUID       NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    grade_id    UUID       NOT NULL REFERENCES grade(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (teacher_id, grade_id)
);

CREATE TABLE IF NOT EXISTS student (
    id          UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name  VARCHAR(100)  NOT NULL,
    middle_name VARCHAR(100),
    last_name   VARCHAR(100)  NOT NULL,
    school_id   VARCHAR(256)  NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS session (
    id          UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    title       VARCHAR(256)   NOT NULL,
    start_at    TIMESTAMPTZ    NOT NULL,
    duration    INT            NOT NULL,
    status      session_status NOT NULL DEFAULT 'Pending',
    created_at  TIMESTAMPTZ    NOT NULL DEFAULT now(),
    creator_id  UUID           NOT NULL REFERENCES "user"(id) ON DELETE RESTRICT,
    teacher_id  UUID           NOT NULL REFERENCES "user"(id) ON DELETE RESTRICT,
    grade_id    UUID           NOT NULL REFERENCES grade(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS attendance (
    id          UUID               PRIMARY KEY DEFAULT gen_random_uuid(),
    status      attendance_status  NOT NULL,
    reason      TEXT,
    session_id  UUID               NOT NULL REFERENCES session(id) ON DELETE CASCADE,
    student_id  UUID               NOT NULL REFERENCES student(id) ON DELETE CASCADE,
    UNIQUE (session_id, student_id)
);

CREATE TABLE IF NOT EXISTS bathroom_log (
    id          UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  UUID          NOT NULL REFERENCES session(id) ON DELETE CASCADE,
    student_id  UUID          NOT NULL REFERENCES student(id) ON DELETE CASCADE,
    started_at  TIMESTAMPTZ   NOT NULL DEFAULT now(),
    duration    DECIMAL(6,2),
    set_by      UUID          NOT NULL REFERENCES "user"(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS behavior (
    id      UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    type    behavior_type  NOT NULL,
    tag     VARCHAR(100)   NOT NULL,
    point   INT            NOT NULL DEFAULT 0 CHECK (point >= 0)
);

CREATE TABLE IF NOT EXISTS session_student_behavior (
    id           UUID   PRIMARY KEY DEFAULT gen_random_uuid(),
    comment      TEXT,
    conseqence   TEXT,
    session_id   UUID   NOT NULL REFERENCES session(id) ON DELETE CASCADE,
    student_id   UUID   NOT NULL REFERENCES student(id) ON DELETE CASCADE,
    behavior_id  UUID   NOT NULL REFERENCES behavior(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS event_log (
    id                UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type        event_type   NOT NULL,
    session_id        UUID         REFERENCES session(id) ON DELETE CASCADE,
    teacher_grade_id  UUID         REFERENCES teacher_grade(id) ON DELETE CASCADE,
    triggered_by      UUID         NOT NULL REFERENCES "user"(id) ON DELETE RESTRICT,
    metadata          JSONB,
    occurred_at       TIMESTAMPTZ  NOT NULL DEFAULT now()
);
"""


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Runs once per test session, after pytest-django's normal setup —
    this is the documented way to extend it, per pytest-django's docs."""
    with django_db_blocker.unblock():
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(TEST_SCHEMA_SQL)
    yield


# ============================================================
# Factory fixtures
# ============================================================

@pytest.fixture
def admin_user(db):
    return AppUser.objects.create(
        id=uuid.uuid4(), first_name="Ada", last_name="Min", email="admin@example.com", role="Admin"
    )


@pytest.fixture
def teacher_user(db):
    return AppUser.objects.create(
        id=uuid.uuid4(), first_name="Tina", last_name="Teach", email="teacher@example.com", role="Teacher"
    )


@pytest.fixture
def other_teacher_user(db):
    return AppUser.objects.create(
        id=uuid.uuid4(), first_name="Omar", last_name="Other", email="other@example.com", role="Teacher"
    )


@pytest.fixture
def grade(db):
    return Grade.objects.create(level=5, section="A")


@pytest.fixture
def student(db):
    return Student.objects.create(first_name="Sam", last_name="Student", school_id="S-0001")


@pytest.fixture
def behavior_positive(db):
    return Behavior.objects.create(type="Positive", tag="Helped a classmate", point=5)


@pytest.fixture
def behavior_negative(db):
    return Behavior.objects.create(type="Negative", tag="Talking out of turn", point=2)


@pytest.fixture
def session_pending(db, teacher_user, admin_user, grade):
    return Session.objects.create(
        title="Math - Period 1",
        start_at=timezone.now(),
        duration=45,
        creator=admin_user,
        teacher=teacher_user,
        grade=grade,
        status=SessionStatus.PENDING,
    )


@pytest.fixture
def api_client():
    return APIClient()


def _authed_client(user, token="test_token"):
    client = APIClient()
    # bypasses SupabaseAuthentication entirely — standard DRF test pattern
    client.force_authenticate(user=user, token=token)
    return client


@pytest.fixture
def as_admin(admin_user):
    return _authed_client(admin_user)


@pytest.fixture
def as_teacher(teacher_user):
    return _authed_client(teacher_user)


@pytest.fixture
def as_other_teacher(other_teacher_user):
    return _authed_client(other_teacher_user)


# ============================================================
# Bathroom start/stop fixtures
# ============================================================

@pytest.fixture
def session_of_other_teacher(db, other_teacher_user, admin_user, grade):
    return Session.objects.create(
        title="Other Teacher's Session",
        start_at=timezone.now(),
        duration=45,
        creator=admin_user,
        teacher=other_teacher_user,
        grade=grade,
        status=SessionStatus.PENDING,
    )


@pytest.fixture
def bathroom_log(db, session_pending, student, teacher_user):
    """An OPEN trip (duration=None) on teacher_user's own session."""
    return BathroomLog.objects.create(
        session=session_pending,
        student=student,
        set_by=teacher_user,
    )


@pytest.fixture
def closed_bathroom_log(db, session_pending, student, teacher_user):
    """A CLOSED trip (duration already set) on teacher_user's own session."""
    return BathroomLog.objects.create(
        session=session_pending,
        student=student,
        set_by=teacher_user,
        duration="5.00",
    )


@pytest.fixture
def bathroom_log_of_other_teacher(db, session_of_other_teacher, student, other_teacher_user):
    """An open trip belonging to a DIFFERENT teacher's session — used to
    prove as_teacher can't reach it."""
    return BathroomLog.objects.create(
        session=session_of_other_teacher,
        student=student,
        set_by=other_teacher_user,
    )
