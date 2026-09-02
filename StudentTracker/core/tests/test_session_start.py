import pytest
from django.urls import reverse

from core.models import EventLog

pytestmark = pytest.mark.django_db


def test_requires_auth(api_client, session_pending):
    resp = api_client.post(reverse("session-start", args=[session_pending.id]))
    assert resp.status_code == 401


def test_not_your_session(as_other_teacher, session_pending):
    resp = as_other_teacher.post(
        reverse("session-start", args=[session_pending.id]))
    assert resp.status_code == 404


def test_starts_a_pending_session(as_teacher, session_pending):
    resp = as_teacher.post(reverse("session-start", args=[session_pending.id]))
    assert resp.status_code == 200
    session_pending.refresh_from_db()
    assert session_pending.status == "Running"


def test_logs_a_session_started_event(as_teacher, session_pending):
    as_teacher.post(reverse("session-start", args=[session_pending.id]))
    assert EventLog.objects.filter(
        event_type="session_started", session=session_pending).exists()


def test_cannot_start_a_running_session_again(as_teacher, session_pending):
    as_teacher.post(reverse("session-start", args=[session_pending.id]))
    resp = as_teacher.post(reverse("session-start", args=[session_pending.id]))
    assert resp.status_code == 409


def test_cannot_start_a_finished_session(as_teacher, session_pending):
    session_pending.status = "Finished"
    session_pending.save(update_fields=["status"])
    resp = as_teacher.post(reverse("session-start", args=[session_pending.id]))
    assert resp.status_code == 409
