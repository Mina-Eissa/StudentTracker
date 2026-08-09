from rest_framework import viewsets, permissions

from ..models import Student
from ..serializers import StudentSerializer


class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Student.objects.all().order_by("last_name")
