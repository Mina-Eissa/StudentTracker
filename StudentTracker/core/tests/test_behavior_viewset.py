import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_requires_auth(api_client):
    resp = api_client.get(reverse("behavior-tag-list"))
    assert resp.status_code == 401


def test_any_authenticated_can_list(as_teacher, behavior_positive):
    resp = as_teacher.get(reverse("behavior-tag-list"))
    assert resp.status_code == 200


def test_teacher_cannot_create(as_teacher):
    resp = as_teacher.post(reverse("behavior-tag-list"),
                           {"type": "Positive", "tag": "Great job", "point": 3}, format="json")
    assert resp.status_code == 403


def test_admin_can_create(as_admin):
    resp = as_admin.post(reverse("behavior-tag-list"),
                         {"type": "Positive", "tag": "Great job", "point": 3}, format="json")
    assert resp.status_code == 201
