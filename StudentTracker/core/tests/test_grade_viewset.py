import pytest
from django.urls import reverse

from core.models import TeacherGrade

pytestmark = pytest.mark.django_db


def test_requires_auth(api_client):
    resp = api_client.get(reverse("grade-list"))
    assert resp.status_code == 401


def test_teacher_sees_only_assigned_grades(as_teacher, teacher_user, grade):
    resp = as_teacher.get(reverse("grade-list"))
    assert resp.data["results"] == [] if "results" in resp.data else resp.data == []

    TeacherGrade.objects.create(teacher=teacher_user, grade=grade)
    resp2 = as_teacher.get(reverse("grade-list"))
    ids = [row["id"] for row in (resp2.data["results"] if "results" in resp2.data else resp2.data)]
    assert str(grade.id) in ids


def test_admin_sees_all_grades(as_admin, grade):
    resp = as_admin.get(reverse("grade-list"))
    ids = [row["id"] for row in (resp.data["results"] if "results" in resp.data else resp.data)]
    assert str(grade.id) in ids


def test_teacher_cannot_create_grade(as_teacher):
    resp = as_teacher.post(reverse("grade-list"), {"level": 6, "section": "B"}, format="json")
    assert resp.status_code == 403


def test_admin_can_create_grade(as_admin):
    resp = as_admin.post(reverse("grade-list"), {"level": 6, "section": "B"}, format="json")
    assert resp.status_code == 201
