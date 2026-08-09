from rest_framework import viewsets

from ..models import Behavior
from ..serializers import BehaviorSerializer
from ..permissions import IsAdminOrReadOnly


class BehaviorViewSet(viewsets.ModelViewSet):
    """The behavior catalog (tags + point values) — any teacher can read it,
    only Admins can add/edit/remove entries."""

    serializer_class = BehaviorSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Behavior.objects.all()
