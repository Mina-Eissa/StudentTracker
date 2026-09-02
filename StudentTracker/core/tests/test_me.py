import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_me_requires_auth(api_client):
    resp = api_client.get(reverse("me"))
    assert resp.status_code == 401


def test_me_returns_own_profile(as_teacher, teacher_user):
    resp = as_teacher.get(reverse("me"))
    assert resp.status_code == 200
    assert resp.data["id"] == str(teacher_user.id)
    assert resp.data["role"] == "Teacher"
