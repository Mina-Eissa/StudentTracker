import pytest
from django.urls import reverse
from django.utils import timezone

from core.models import EventLog, Session

pytestmark = pytest.mark.django_db


def test_requires_auth(api_client):
    resp = api_client.get(reverse("session-list"))
    assert resp.status_code == 401


def test_teacher_only_sees_own_sessions(as_teacher, as_other_teacher, session_pending):
    resp = as_teacher.get(reverse("session-list"))
    assert len(resp.data["results"]) if "results" in resp.data else len(resp.data)
    ids = [row["id"] for row in (resp.data["results"] if "results" in resp.data else resp.data)]
    assert str(session_pending.id) in ids

    resp2 = as_other_teacher.get(reverse("session-list"))
    ids2 = [row["id"] for row in (resp2.data["results"] if "results" in resp2.data else resp2.data)]
    assert str(session_pending.id) not in ids2


def test_admin_sees_all_sessions(as_admin, session_pending):
    resp = as_admin.get(reverse("session-list"))
    ids = [row["id"] for row in (resp.data["results"] if "results" in resp.data else resp.data)]
    assert str(session_pending.id) in ids


def test_create_defaults_teacher_and_creator_to_caller(as_teacher, teacher_user, grade):
    resp = as_teacher.post(reverse("session-list"), {
        "title": "Science - Period 2",
        "start_at": timezone.now().isoformat(),
        "duration": 40,
        "grade": str(grade.id),
    }, format="json")
    assert resp.status_code == 201
    session = Session.objects.get(id=resp.data["id"])
    assert session.teacher_id == teacher_user.id
    assert session.creator_id == teacher_user.id
    assert session.status == "Pending"


def test_create_fires_session_set_event(as_teacher, grade):
    resp = as_teacher.post(reverse("session-list"), {
        "title": "History - Period 3",
        "start_at": timezone.now().isoformat(),
        "duration": 40,
        "grade": str(grade.id),
    }, format="json")
    assert EventLog.objects.filter(event_type="session_set", session_id=resp.data["id"]).exists()


def test_teacher_cannot_update_another_teachers_session(as_other_teacher, session_pending):
    resp = as_other_teacher.patch(reverse("session-detail", args=[session_pending.id]), {"title": "Hijacked"}, format="json")
    assert resp.status_code in (403, 404)
