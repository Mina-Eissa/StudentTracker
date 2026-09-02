import pytest
from django.urls import reverse

from core.models import AppUser

pytestmark = pytest.mark.django_db


def _mock_resp(mocker, status_code, json_data):
    resp = mocker.Mock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    return resp


def test_non_admin_forbidden(as_teacher):
    resp = as_teacher.post(reverse("create-user"), {
        "email": "x@example.com", "first_name": "A", "last_name": "B", "role": "Teacher",
    }, format="json")
    assert resp.status_code == 403


def test_missing_fields(as_admin):
    resp = as_admin.post(reverse("create-user"),
                         {"email": "x@example.com"}, format="json")
    assert resp.status_code == 400


def test_invalid_role(as_admin):
    resp = as_admin.post(reverse("create-user"), {
        "email": "x@example.com", "first_name": "A", "last_name": "B", "role": "Superuser",
    }, format="json")
    assert resp.status_code == 400


def test_invite_path_default_when_no_password(mocker, as_admin):
    new_id = "33333333-3333-3333-3333-333333333333"
    mock_post = mocker.patch(
        "core.views.create_new_user.requests.post",
        return_value=_mock_resp(mocker, 200, {"id": new_id}),
    )
    resp = as_admin.post(reverse("create-user"), {
        "email": "invitee@example.com", "first_name": "In", "last_name": "Vitee", "role": "Teacher",
    }, format="json")
    assert resp.status_code == 201
    assert "invite" in resp.data["note"].lower()
    called_url = mock_post.call_args[0][0]
    assert "/auth/v1/invite" in called_url
    assert AppUser.objects.filter(id=new_id).exists()


def test_password_fallback_path(mocker, as_admin):
    new_id = "44444444-4444-4444-4444-444444444444"
    mock_post = mocker.patch(
        "core.views.create_new_user.requests.post",
        return_value=_mock_resp(mocker, 200, {"id": new_id}),
    )
    resp = as_admin.post(reverse("create-user"), {
        "email": "pwuser@example.com", "first_name": "Pw", "last_name": "User",
        "role": "Teacher", "password": "somepassword123",
    }, format="json")
    assert resp.status_code == 201
    assert "note" not in resp.data or "password" in resp.data.get(
        "note", "").lower()
    called_url = mock_post.call_args[0][0]
    assert "/auth/v1/admin/users" in called_url


def test_password_too_short(as_admin):
    resp = as_admin.post(reverse("create-user"), {
        "email": "x@example.com", "first_name": "A", "last_name": "B",
        "role": "Teacher", "password": "short",
    }, format="json")
    assert resp.status_code == 400


def test_rolls_back_auth_user_if_profile_creation_fails(mocker, as_admin, teacher_user):
    # reuse an email that already exists on AppUser -> profile create will
    # violate the unique email constraint, triggering the rollback path
    new_id = "55555555-5555-5555-5555-555555555555"
    mocker.patch(
        "core.views.create_new_user.requests.post",
        return_value=_mock_resp(mocker, 200, {"id": new_id}),
    )
    mock_delete = mocker.patch("core.views.create_new_user.requests.delete")
    resp = as_admin.post(reverse("create-user"), {
        "email": teacher_user.email,  # duplicate -> IntegrityError on create
        "first_name": "Dup", "last_name": "User", "role": "Teacher",
    }, format="json")
    assert resp.status_code == 500
    mock_delete.assert_called_once()
    assert not AppUser.objects.filter(id=new_id).exists()
