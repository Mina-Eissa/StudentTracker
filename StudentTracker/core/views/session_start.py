from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Session
from ..signals import session_started


class StartSessionView(APIView):
    """POST /api/sessions/<session_id>/start/  — Pending -> Running"""

    def post(self, request, session_id):
        session = Session.objects.filter(id=session_id, teacher_id=request.user.id).first()
        if not session:
            return Response({"detail": "Session not found or not yours."}, status=404)

        if session.status != "Pending":
            return Response({"detail": f"Session is {session.status}, cannot start."}, status=409)

        session.status = "Running"
        session.save(update_fields=["status"])

        session_started.send(sender=Session, session=session, triggered_by=request.user)

        return Response({"status": "Running"})
