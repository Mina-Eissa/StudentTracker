import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_requires_auth(api_client):
    resp = api_client.get(reverse("attendance-list"))
    assert resp.status_code == 401


def test_teacher_can_mark_attendance_for_own_session(as_teacher, session_pending, student):
    resp = as_teacher.post(reverse("attendance-list"), {
        "session": str(session_pending.id), "student": str(student.id), "status": "Present",
    }, format="json")
    assert resp.status_code == 201


def test_teacher_cannot_mark_attendance_for_another_teachers_session(as_other_teacher, session_pending, student):
    resp = as_other_teacher.post(reverse("attendance-list"), {
        "session": str(session_pending.id), "student": str(student.id), "status": "Present",
    }, format="json")
    # session isn't visible to this caller at all through the scoped queryset
    assert resp.status_code in (400, 403, 404)


def test_duplicate_attendance_for_same_student_session_rejected(as_teacher, session_pending, student):
    as_teacher.post(reverse("attendance-list"), {
        "session": str(session_pending.id), "student": str(student.id), "status": "Present",
    }, format="json")
    resp = as_teacher.post(reverse("attendance-list"), {
        "session": str(session_pending.id), "student": str(student.id), "status": "Late",
    }, format="json")
    assert resp.status_code == 400


def test_other_teacher_does_not_see_this_attendance_in_list(as_teacher, as_other_teacher, session_pending, student):
    as_teacher.post(reverse("attendance-list"), {
        "session": str(session_pending.id), "student": str(student.id), "status": "Present",
    }, format="json")
    resp = as_other_teacher.get(reverse("attendance-list"))
    rows = resp.data["results"] if "results" in resp.data else resp.data
    assert rows == []
