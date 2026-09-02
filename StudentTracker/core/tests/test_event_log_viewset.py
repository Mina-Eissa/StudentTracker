import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_requires_auth(api_client):
    resp = api_client.get(reverse("event-log-list"))
    assert resp.status_code == 401


def test_teacher_sees_events_from_own_sessions(as_teacher, session_pending):
    as_teacher.post(reverse("session-start", args=[session_pending.id]))
    resp = as_teacher.get(reverse("event-log-list"))
    rows = resp.data["results"] if "results" in resp.data else resp.data
    assert any(row["event_type"] == "session_started" for row in rows)


def test_other_teacher_does_not_see_them(as_teacher, as_other_teacher, session_pending):
    as_teacher.post(reverse("session-start", args=[session_pending.id]))
    resp = as_other_teacher.get(reverse("event-log-list"))
    rows = resp.data["results"] if "results" in resp.data else resp.data
    assert rows == []


def test_admin_sees_everything(as_teacher, as_admin, session_pending):
    as_teacher.post(reverse("session-start", args=[session_pending.id]))
    resp = as_admin.get(reverse("event-log-list"))
    rows = resp.data["results"] if "results" in resp.data else resp.data
    assert any(row["event_type"] == "session_started" for row in rows)


def test_read_only_no_create(as_admin):
    resp = as_admin.post(reverse("event-log-list"), {"event_type": "session_set"}, format="json")
    assert resp.status_code == 405
