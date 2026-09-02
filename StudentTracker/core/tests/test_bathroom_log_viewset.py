import pytest
from django.urls import reverse

from core.models import BathroomLog

pytestmark = pytest.mark.django_db


@pytest.fixture
def closed_log(session_pending, student, teacher_user):
    return BathroomLog.objects.create(session=session_pending, student=student, set_by=teacher_user, duration="4.50")


def test_requires_auth(api_client, closed_log):
    resp = api_client.get(reverse("bathroom-log-list"))
    assert resp.status_code == 401


def test_teacher_sees_own_sessions_trips(as_teacher, closed_log):
    resp = as_teacher.get(reverse("bathroom-log-list"))
    rows = resp.data["results"] if "results" in resp.data else resp.data
    assert any(row["id"] == str(closed_log.id) for row in rows)


def test_other_teacher_does_not_see_it(as_other_teacher, closed_log):
    resp = as_other_teacher.get(reverse("bathroom-log-list"))
    rows = resp.data["results"] if "results" in resp.data else resp.data
    assert rows == []


# def test_filter_by_student(as_teacher, closed_log, student):
#     resp = as_teacher.get(reverse("bathroom-log-list"),
#                           {"student": str(student.id)})
#     rows = resp.data["results"] if "results" in resp.data else resp.data
#     assert all(row["student"] == str(student.id) for row in rows)

# ***** No one can patch or update bathroom log ******

# def test_owning_teacher_can_patch_duration(as_teacher, closed_log):
#     resp = as_teacher.patch(reverse(
#         "bathroom-log-detail", args=[closed_log.id]), {"duration": "7.25"}, format="json")
#     assert resp.status_code == 200
#     closed_log.refresh_from_db()
#     assert float(closed_log.duration) == 7.25


# def test_other_teacher_cannot_patch_it(as_other_teacher, closed_log):
#     resp = as_other_teacher.patch(reverse(
#         "bathroom-log-detail", args=[closed_log.id]), {"duration": "1.00"}, format="json")
#     assert resp.status_code == 404


# def test_negative_duration_rejected(as_teacher, closed_log):
#     resp = as_teacher.patch(reverse(
#         "bathroom-log-detail", args=[closed_log.id]), {"duration": "-3"}, format="json")
#     assert resp.status_code == 400


def test_teacher_cannot_delete(as_teacher, closed_log):
    resp = as_teacher.delete(
        reverse("bathroom-log-detail", args=[closed_log.id]))
    assert resp.status_code == 403


def test_admin_can_delete(as_admin, closed_log):
    resp = as_admin.delete(
        reverse("bathroom-log-detail", args=[closed_log.id]))
    assert resp.status_code == 204
    assert not BathroomLog.objects.filter(id=closed_log.id).exists()


def test_cannot_create_via_viewset_post(as_teacher, session_pending, student):
    resp = as_teacher.post(reverse("bathroom-log-list"), {
        "session": str(session_pending.id), "student": str(student.id),
    }, format="json")
    assert resp.status_code == 405  # creation only via /api/v1/bathroom-start
