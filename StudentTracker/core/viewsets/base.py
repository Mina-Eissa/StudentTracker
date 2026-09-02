from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from ..models import Session


class SessionScopedViewSet(viewsets.ModelViewSet):
    """
    Shared base for anything hanging off a session.

    Admins can access all sessions.
    Teachers can only access sessions they own.
    """

    permission_classes = [permissions.IsAuthenticated]
    session_field = "session"

    def _owned_session_ids(self):
        user = self.request.user

        if user.role == "Admin":
            return Session.objects.values_list("id", flat=True)

        return Session.objects.filter(
            teacher_id=user.id
        ).values_list("id", flat=True)

    def get_queryset(self):
        return self.queryset.filter(
            **{
                f"{self.session_field}_id__in": self._owned_session_ids()
            }
        )

    def perform_create(self, serializer):
        session = serializer.validated_data["session"]

        if (
            self.request.user.role != "Admin"
            and session.teacher_id != self.request.user.id
        ):
            raise PermissionDenied(
                "You can only create records for your own sessions."
            )

        serializer.save()

    def perform_update(self, serializer):
        session = serializer.instance.session

        if (
            self.request.user.role != "Admin"
            and session.teacher_id != self.request.user.id
        ):
            raise PermissionDenied(
                "You can only modify records for your own sessions."
            )

        serializer.save()
