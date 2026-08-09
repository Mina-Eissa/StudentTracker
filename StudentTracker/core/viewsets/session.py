from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied

from ..models import Session
from ..serializers import SessionSerializer


class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "Admin":
            return Session.objects.all()
        return Session.objects.filter(teacher_id=user.id)

    def perform_create(self, serializer):
        # default the session's teacher to whoever is creating it, unless an
        # admin explicitly assigns a different teacher in the payload
        teacher_id = self.request.data.get("teacher") or self.request.user.id
        serializer.save(creator_id=self.request.user.id, teacher_id=teacher_id)

    def perform_update(self, serializer):
        session = self.get_object()
        if self.request.user.role != "Admin" and session.teacher_id != self.request.user.id:
            raise PermissionDenied("You can only edit your own sessions.")
        serializer.save()
