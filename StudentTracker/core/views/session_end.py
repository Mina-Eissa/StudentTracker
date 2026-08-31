from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Session
from ..signals import session_ended


class EndSessionView(APIView):
    """POST /api/sessions/<session_id>/end/

    Marks the session finished and announces it. Force-closing open bathroom
    logs is NOT done here anymore — that reaction lives in receivers.py and
    fires independently. This view doesn't import BathroomLog at all.
    """

    def post(self, request, session_id):
        session = Session.objects.filter(id=session_id, teacher_id=request.user.id).first()
        if not session:
            return Response({"detail": "Session not found or not yours."}, status=404)

        if session.status == "finished":
            return Response({"detail": "Session is already finished."}, status=409)

        session.status = "finished"
        session.save(update_fields=["status"])

        session_ended.send(sender=Session, session=session, triggered_by=request.user)

        return Response({"status": "finished"})
