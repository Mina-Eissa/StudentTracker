from rest_framework import viewsets

from ..models import Subject
from ..serializers import SubjectSerializer
from ..permissions import IsAdminOrReadOnly


class SubjectViewSet(viewsets.ModelViewSet):
    """The subject catalog (e.g. Math, Science) — any authenticated user
    can read it, only Admins can add/edit/remove entries."""

    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Subject.objects.all().order_by("name")
