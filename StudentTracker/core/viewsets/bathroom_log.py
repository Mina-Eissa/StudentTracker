from ..models import BathroomLog
from ..serializers import BathroomLogSerializer
from .base import SessionScopedViewSet


class BathroomLogViewSet(SessionScopedViewSet):
    """Read-only here — writes only happen through /bathroom/start/ and /bathroom/stop/
    so count_times/duration_each_time stay correctly computed."""

    serializer_class = BathroomLogSerializer
    queryset = BathroomLog.objects.all()
    http_method_names = ["get", "head"]
