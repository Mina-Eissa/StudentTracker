from rest_framework import viewsets

from ..models import Grade, TeacherGrade
from ..serializers import GradeSerializer
from ..permissions import IsAdminOrReadOnly


class GradeViewSet(viewsets.ModelViewSet):
    serializer_class = GradeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.role == "Admin":
            return Grade.objects.all()
        # teachers only see grades they're assigned to via teacher_grade
        assigned_ids = TeacherGrade.objects.filter(
            teacher_id=user.id).values_list("grade_id", flat=True)
        return Grade.objects.filter(id__in=assigned_ids)
