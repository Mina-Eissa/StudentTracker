from rest_framework import viewsets

from ..models import TeacherGrade
from ..serializers import TeacherGradeSerializer
from ..permissions import IsAdmin
from ..signals import grade_assigned


class TeacherGradeViewSet(viewsets.ModelViewSet):
    """Admin-only: assigning teachers to grades."""

    serializer_class = TeacherGradeSerializer
    permission_classes = [IsAdmin]
    queryset = TeacherGrade.objects.all()

    def perform_create(self, serializer):
        teacher_grade = serializer.save()
        grade_assigned.send(
            sender=TeacherGrade, teacher_grade=teacher_grade, triggered_by=self.request.user)
