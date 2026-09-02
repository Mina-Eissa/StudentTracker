import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_requires_auth(api_client):
    resp = api_client.get(reverse("behavior-event-list"))
    assert resp.status_code == 401


def test_teacher_can_log_behavior_for_own_session(as_teacher, session_pending, student, behavior_negative):
    resp = as_teacher.post(reverse("behavior-event-list"), {
        "session": str(session_pending.id), "student": str(student.id),
        "behavior": str(behavior_negative.id), "comment": "Talked during quiz",
        "consequence": "Verbal warning",
    }, format="json")
    assert resp.status_code == 201
    assert resp.data["consequence"] == "Verbal warning"


def test_other_teacher_cannot_log_for_this_session(as_other_teacher, session_pending, student, behavior_negative):
    resp = as_other_teacher.post(reverse("behavior-event-list"), {
        "session": str(session_pending.id), "student": str(student.id), "behavior": str(behavior_negative.id),
    }, format="json")
    assert resp.status_code in (400, 403, 404)


def test_other_teacher_does_not_see_it_in_list(as_teacher, as_other_teacher, session_pending, student, behavior_negative):
    as_teacher.post(reverse("behavior-event-list"), {
        "session": str(session_pending.id), "student": str(student.id), "behavior": str(behavior_negative.id),
    }, format="json")
    resp = as_other_teacher.get(reverse("behavior-event-list"))
    rows = resp.data["results"] if "results" in resp.data else resp.data
    assert rows == []
