# import pytest
# from django.urls import reverse

# from core.models import Attendance, BathroomLog, SessionStudentBehavior

# pytestmark = pytest.mark.django_db


# def test_requires_auth(api_client, session_pending):
#     resp = api_client.get(reverse("session-report", args=[session_pending.id]))
#     assert resp.status_code == 401


# def test_not_your_session(as_other_teacher, session_pending):
#     resp = as_other_teacher.get(reverse("session-report", args=[session_pending.id]))
#     assert resp.status_code == 404


# def test_report_aggregates_all_three_categories(as_teacher, session_pending, student, teacher_user, behavior_positive):
#     Attendance.objects.create(session=session_pending, student=student, status="Present")
#     SessionStudentBehavior.objects.create(session=session_pending, student=student, behavior=behavior_positive)
#     BathroomLog.objects.create(session=session_pending, student=student, set_by=teacher_user, duration="6.00")

#     resp = as_teacher.get(reverse("session-report", args=[session_pending.id]))
#     assert resp.status_code == 200
#     assert len(resp.data["attendance"]) == 1
#     assert len(resp.data["behavior_totals"]) == 1
#     assert resp.data["behavior_totals"][0]["positive_count"] == 1
#     assert resp.data["behavior_totals"][0]["total_points"] == behavior_positive.point
#     assert len(resp.data["bathroom"]) == 1


# def test_report_is_empty_shaped_for_a_session_with_no_activity(as_teacher, session_pending):
#     resp = as_teacher.get(reverse("session-report", args=[session_pending.id]))
#     assert resp.status_code == 200
#     assert resp.data["attendance"] == []
#     assert resp.data["behavior_totals"] == []
#     assert resp.data["bathroom"] == []
