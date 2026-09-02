import pytest
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from core.models import Session, SessionStudentBehavior

pytestmark = pytest.mark.django_db


def test_requires_auth(api_client, student):
    resp = api_client.get(reverse("student-behavior-summary", args=[student.id]))
    assert resp.status_code == 401


def test_totals_across_sessions(as_teacher, teacher_user, admin_user, grade, student, behavior_positive, behavior_negative):
    s1 = Session.objects.create(title="S1", start_at=timezone.now(), duration=30, creator=admin_user, teacher=teacher_user, grade=grade)
    s2 = Session.objects.create(title="S2", start_at=timezone.now(), duration=30, creator=admin_user, teacher=teacher_user, grade=grade)
    SessionStudentBehavior.objects.create(session=s1, student=student, behavior=behavior_positive)
    SessionStudentBehavior.objects.create(session=s2, student=student, behavior=behavior_negative)

    resp = as_teacher.get(reverse("student-behavior-summary", args=[student.id]))
    assert resp.status_code == 200
    assert resp.data["totals"]["positive_count"] == 1
    assert resp.data["totals"]["negative_count"] == 1
    assert resp.data["totals"]["total_points"] == behavior_positive.point + behavior_negative.point
    assert len(resp.data["events"]) == 2


def test_date_range_filter_excludes_out_of_range_events(as_teacher, teacher_user, admin_user, grade, student, behavior_positive):
    old_session = Session.objects.create(
        title="Old", start_at=timezone.now() - timedelta(days=60), duration=30,
        creator=admin_user, teacher=teacher_user, grade=grade,
    )
    SessionStudentBehavior.objects.create(session=old_session, student=student, behavior=behavior_positive)

    resp = as_teacher.get(reverse("student-behavior-summary", args=[student.id]), {
        "date_from": timezone.now().date().isoformat(),
    })
    assert resp.data["totals"]["positive_count"] == 0
    assert resp.data["events"] == []


def test_summary_scoped_to_callers_own_sessions(as_teacher, as_other_teacher, other_teacher_user, admin_user, grade, student, behavior_positive):
    other_session = Session.objects.create(
        title="Other's class", start_at=timezone.now(), duration=30,
        creator=admin_user, teacher=other_teacher_user, grade=grade,
    )
    SessionStudentBehavior.objects.create(session=other_session, student=student, behavior=behavior_positive)

    resp = as_teacher.get(reverse("student-behavior-summary", args=[student.id]))
    assert resp.data["totals"]["positive_count"] == 0
