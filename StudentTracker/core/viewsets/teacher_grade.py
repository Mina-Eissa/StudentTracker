from rest_framework import viewsets

from ..models import TeacherGrade
from ..serializers import TeacherGradeSerializer
from ..permissions import IsAdmin


class TeacherGradeViewSet(viewsets.ModelViewSet):
    """Admin-only: assigning teachers to grades."""

    serializer_class = TeacherGradeSerializer
    permission_classes = [IsAdmin]
    queryset = TeacherGrade.objects.all()
