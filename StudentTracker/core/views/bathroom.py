
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.authentication import SupabaseAuthentication
from ..models import Session, BathroomLog


class BathroomStartView(APIView):
    """POST { session_id, student_id } -> marks a student as 'out'.
    If they are already out, returns 409 Conflict.
    If they are not out, creates a new BathroomLog with duration=None and returns 201 Created.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [SupabaseAuthentication]

    def post(self, request):
        session_id = request.data.get("session_id")
        student_id = request.data.get("student_id")
        if not session_id or not student_id:
            return Response({"detail": "session_id and student_id are required."}, status=400)

        session = Session.objects.filter(
            id=session_id, teacher_id=request.user.id).first()
        if not session:
            return Response({"detail": "Session not found or not yours."}, status=404)
        open_trip = BathroomLog.objects.filter(
            session_id=session_id, student_id=student_id, duration__isnull=True).first()
        if open_trip:
            return Response({"detail": "There is already an open bathroom trip for this student."}, status=409)

        bathroom_trip = BathroomLog.objects.create(
            session_id=session_id,
            student_id=student_id,
            set_by=request.user
        )

        return Response({"action": "started", "is_open": True, "id": str(bathroom_trip.id), "started_at": bathroom_trip.started_at}, status=201)


class BathroomStopView(APIView):
    """POST { id } -> closes the timer, updates bathroom_log."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [SupabaseAuthentication]

    def post(self, request):
        trip_id = request.data.get("id")

        bathroom_trip = BathroomLog.objects.filter(
            id=trip_id,
            session__teacher_id=request.user.id
        ).first()
        if not bathroom_trip:
            return Response({"detail": "Bathroom log not found."}, status=404)

        if not bathroom_trip.is_open:
            return Response({"detail": "No open bathroom timer for this student."}, status=409)

        time_elapsed = timezone.now() - bathroom_trip.started_at
        duration_minutes = time_elapsed.total_seconds() / 60.0
        bathroom_trip.duration = round(duration_minutes, 2)
        bathroom_trip.save(update_fields=["duration"])
        return Response({"detail": "Bathroom timer stopped."}, status=200)
