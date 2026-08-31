from django.db.models import Q
from rest_framework import viewsets, permissions

from ..models import EventLog
from ..serializers import EventLogSerializer


class EventLogViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/event-logs/ — Admin sees everything; a teacher sees events
    tied to their own sessions or their own grade assignments."""

    serializer_class = EventLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = EventLog.objects.all()
        if user.role == "Admin":
            return qs
        return qs.filter(Q(session__teacher_id=user.id) | Q(teacher_grade__teacher_id=user.id))
