from rest_framework import viewsets
from core.permissions import IsAdminOrReadOnly
from core.models import AcademicYear
from core.serializers import AcademicYearSerializer


class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [IsAdminOrReadOnly]
