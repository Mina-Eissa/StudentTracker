from rest_framework import viewsets, permissions

from ..models import Session


class SessionScopedViewSet(viewsets.ModelViewSet):
    """Shared base for anything hanging off a session — restricts rows to
    sessions the caller owns (or everything, if Admin)."""

    permission_classes = [permissions.IsAuthenticated]
    session_field = "session_id"

    def _owned_session_ids(self):
        user = self.request.user
        if user.role == "Admin":
            return Session.objects.values_list("id", flat=True)
        return Session.objects.filter(teacher_id=user.id).values_list("id", flat=True)

    def get_queryset(self):
        return self.queryset.filter(**{f"{self.session_field}__in": self._owned_session_ids()})
