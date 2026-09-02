import pytest
from django.urls import reverse

from core.models import EventLog

pytestmark = pytest.mark.django_db


def test_non_admin_forbidden(as_teacher, teacher_user, grade):
    resp = as_teacher.post(reverse("teacher-grade-list"), {
        "teacher": str(teacher_user.id), "grade": str(grade.id),
    }, format="json")
    assert resp.status_code == 403


def test_admin_can_assign_teacher_to_grade(as_admin, teacher_user, grade):
    resp = as_admin.post(reverse("teacher-grade-list"), {
        "teacher": str(teacher_user.id), "grade": str(grade.id),
    }, format="json")
    assert resp.status_code == 201


def test_assignment_fires_grade_assigned_event(as_admin, teacher_user, grade):
    resp = as_admin.post(reverse("teacher-grade-list"), {
        "teacher": str(teacher_user.id), "grade": str(grade.id),
    }, format="json")
    assert EventLog.objects.filter(event_type="grade_assigned", teacher_grade_id=resp.data["id"]).exists()


def test_duplicate_assignment_rejected(as_admin, teacher_user, grade):
    as_admin.post(reverse("teacher-grade-list"), {"teacher": str(teacher_user.id), "grade": str(grade.id)}, format="json")
    resp = as_admin.post(reverse("teacher-grade-list"), {"teacher": str(teacher_user.id), "grade": str(grade.id)}, format="json")
    assert resp.status_code == 400
