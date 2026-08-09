from django.db.models import Count, Sum, Q
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import SessionStudentBehavior


class StudentBehaviorSummaryView(APIView):
    """GET /api/students/<student_id>/behavior-summary/?date_from=&date_to="""

    def get(self, request, student_id):
        qs = SessionStudentBehavior.objects.filter(
            student_id=student_id, session__teacher_id=request.user.id
        )

        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        if date_from:
            qs = qs.filter(session__start_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(session__start_at__date__lte=date_to)

        totals = qs.aggregate(
            total_points=Sum("behavior__point"),
            positive_count=Count("id", filter=Q(behavior__type="Positive")),
            negative_count=Count("id", filter=Q(behavior__type="Negative")),
        )
        events = qs.select_related("behavior", "session").values(
            "session__title",
            "session__start_at",
            "behavior__tag",
            "behavior__type",
            "behavior__point",
            "comment",
            "conseqence",
        )

        return Response({"student_id": student_id, "totals": totals, "events": list(events)})
