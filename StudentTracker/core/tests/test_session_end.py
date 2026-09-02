import pytest
from django.urls import reverse

from core.models import BathroomLog, EventLog, SessionStatus

pytestmark = pytest.mark.django_db


def test_requires_auth(api_client, session_pending):
    resp = api_client.post(reverse("session-end", args=[session_pending.id]))
    assert resp.status_code == 401


def test_not_your_session(as_other_teacher, session_pending):
    resp = as_other_teacher.post(
        reverse("session-end", args=[session_pending.id]))
    assert resp.status_code == 404


def test_ends_a_session(as_teacher, session_pending):
    resp = as_teacher.post(reverse("session-end", args=[session_pending.id]))
    assert resp.status_code == 200
    session_pending.refresh_from_db()
    assert session_pending.status == SessionStatus.FINISHED


def test_cannot_end_an_already_finished_session(as_teacher, session_pending):
    as_teacher.post(reverse("session-end", args=[session_pending.id]))
    resp = as_teacher.post(reverse("session-end", args=[session_pending.id]))
    assert resp.status_code == 409


def test_logs_a_session_ended_event(as_teacher, session_pending):
    as_teacher.post(reverse("session-end", args=[session_pending.id]))
    assert EventLog.objects.filter(
        event_type="session_ended", session=session_pending).exists()


def test_ending_a_session_force_closes_open_bathroom_trips(as_teacher, session_pending, student, teacher_user):
    # simulate an open trip a teacher forgot to stop
    open_log = BathroomLog.objects.create(
        session=session_pending, student=student, set_by=teacher_user)
    assert open_log.duration is None

    as_teacher.post(reverse("session-end", args=[session_pending.id]))

    open_log.refresh_from_db()
    assert open_log.duration is not None
    assert float(open_log.duration) >= 0


def test_ending_a_session_leaves_already_closed_trips_untouched(as_teacher, session_pending, student, teacher_user):
    closed_log = BathroomLog.objects.create(
        session=session_pending, student=student, set_by=teacher_user, duration="5.00"
    )
    as_teacher.post(reverse("session-end", args=[session_pending.id]))
    closed_log.refresh_from_db()
    assert float(closed_log.duration) == 5.00
