from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied

from ..models import Session
from ..serializers import SessionSerializer
from ..signals import session_set


class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "Admin":
            return Session.objects.all()
        return Session.objects.filter(teacher_id=user.id)

    def perform_create(self, serializer):
        teacher_id = self.request.data.get("teacher") or self.request.user.id
        session = serializer.save(
            creator_id=self.request.user.id, teacher_id=teacher_id)
        session_set.send(sender=Session, session=session,
                         triggered_by=self.request.user)

    def perform_update(self, serializer):
        session = self.get_object()
        if self.request.user.role != "Admin" and session.teacher_id != self.request.user.id:
            raise PermissionDenied("You can only edit your own sessions.")
        serializer.save()
