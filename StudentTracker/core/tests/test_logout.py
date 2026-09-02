import pytest
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def _mock_resp(mocker, status_code):
    resp = mocker.Mock()
    resp.status_code = status_code
    resp.text = ""
    return resp


def test_logout_requires_auth():
    resp = APIClient().post(reverse("logout"))
    assert resp.status_code == 401


def test_logout_success(mocker, as_teacher):
    mocker.patch("core.views.logout.requests.post",
                 return_value=_mock_resp(mocker, 204))
    resp = as_teacher.post(reverse("logout"))
    assert resp.status_code == 200


def test_logout_supabase_failure(mocker, as_teacher):
    mocker.patch("core.views.logout.requests.post",
                 return_value=_mock_resp(mocker, 500))
    resp = as_teacher.post(reverse("logout"))
    assert resp.status_code == 400
