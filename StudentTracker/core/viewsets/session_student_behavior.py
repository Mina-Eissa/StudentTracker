from ..models import SessionStudentBehavior
from ..serializers import SessionStudentBehaviorSerializer
from .base import SessionScopedViewSet


class SessionStudentBehaviorViewSet(SessionScopedViewSet):
    serializer_class = SessionStudentBehaviorSerializer
    queryset = SessionStudentBehavior.objects.all()
