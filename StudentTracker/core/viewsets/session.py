from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError

from core.models import Session, AppUser, AcademicYear, Subject, Grade
from ..serializers import SessionSerializer
from ..signals import session_set
from core.pagination import HomeSessionsPagination


class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = HomeSessionsPagination

    def get_queryset(self):
        user = self.request.user
        if user.role == "Admin":
            return Session.objects.all().order_by("start_at", "id")
        return Session.objects.filter(teacher_id=user.id).order_by("start_at", "id")

    def perform_create(self, serializer):
        user = AppUser.objects.get(id=self.request.user.id)
        teacher = serializer.validated_data.get("teacher") or user

        if teacher.role != "Teacher":
            raise PermissionDenied("The specified user is not a teacher.")

        if teacher.pk != user.pk and user.role != "Admin":
            raise PermissionDenied(
                "Only Admin users can create sessions for other teachers."
            )

        academic_year = AcademicYear.objects.filter(current=True).first()
        if academic_year is None:
            raise ValidationError(
                {"academic_year": "No active academic year is set."})

        session = serializer.save(
            creator=user,
            teacher=teacher,
            academic_year=academic_year,
        )
        session_set.send(sender=Session, session=session, triggered_by=user)

    def perform_update(self, serializer):
        session = self.get_object()
        if self.request.user.role != "Admin" and session.teacher_id != self.request.user.id:
            raise PermissionDenied("You can only edit your own sessions.")
        serializer.save()
