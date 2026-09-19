from rest_framework import viewsets
from core.permissions import IsAdminOrReadOnly
from core.serializers import StudentGradeSerializer
from core.models import StudentGrade


class StudentGradeViewSet(viewsets.ModelViewSet):
    serializer_class = StudentGradeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return StudentGrade.objects.select_related("student", "grade").all()
