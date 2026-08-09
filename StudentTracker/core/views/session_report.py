from django.db.models import Count, Sum, Q
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import Session, Attendance, BathroomLog, SessionStudentBehavior


class SessionReportView(APIView):
    """GET /api/sessions/<session_id>/report/
    Attendance + behavior totals + bathroom stats, one student per row."""

    def get(self, request, session_id):
        session = Session.objects.filter(id=session_id, teacher_id=request.user.id).first()
        if not session:
            return Response({"detail": "Session not found or not yours."}, status=404)

        attendance = Attendance.objects.filter(session_id=session_id).values("student_id", "status")

        behavior_totals = (
            SessionStudentBehavior.objects.filter(session_id=session_id)
            .values("student_id")
            .annotate(
                positive_count=Count("id", filter=Q(behavior__type="Positive")),
                negative_count=Count("id", filter=Q(behavior__type="Negative")),
                total_points=Sum("behavior__point"),
            )
        )

        bathroom = BathroomLog.objects.filter(session_id=session_id).values(
            "student_id", "count_times", "duration_each_time"
        )

        return Response({
            "session_id": session_id,
            "attendance": list(attendance),
            "behavior_totals": list(behavior_totals),
            "bathroom": list(bathroom),
        })
