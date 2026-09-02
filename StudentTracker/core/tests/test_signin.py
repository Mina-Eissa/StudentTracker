import pytest
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def _mock_resp(mocker, status_code, json_data):
    resp = mocker.Mock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    return resp


def test_signin_success(mocker, teacher_user):
    mocker.patch(
        "core.views.signin.requests.post",
        return_value=_mock_resp(mocker, 200, {
            "access_token": "tok123", "refresh_token": "refresh123", "expires_in": 3600,
            "user": {"id": str(teacher_user.id)},
        }),
    )
    resp = APIClient().post(reverse("signin"), {
        "email": "teacher@example.com", "password": "secret123"}, format="json")
    assert resp.status_code == 200
    assert resp.data["access_token"] == "tok123"
    assert resp.data["user"]["email"] == "teacher@example.com"


def test_signin_missing_fields():
    resp = APIClient().post(reverse("signin"), {
        "email": "x@example.com"}, format="json")
    assert resp.status_code == 400


def test_signin_invalid_credentials(mocker):
    mocker.patch("core.views.signin.requests.post", return_value=_mock_resp(
        mocker, 400, {"error": "invalid_grant"}))
    resp = APIClient().post(reverse("signin"), {
        "email": "x@example.com", "password": "wrong"}, format="json")
    assert resp.status_code == 401


def test_signin_no_matching_profile(mocker):
    unknown_id = "11111111-1111-1111-1111-111111111111"
    mocker.patch(
        "core.views.signin.requests.post",
        return_value=_mock_resp(mocker, 200, {
            "access_token": "tok", "refresh_token": "r", "expires_in": 3600, "user": {"id": unknown_id},
        }),
    )
    resp = APIClient().post(reverse("signin"), {
        "email": "ghost@example.com", "password": "secret123"}, format="json")
    assert resp.status_code == 403
