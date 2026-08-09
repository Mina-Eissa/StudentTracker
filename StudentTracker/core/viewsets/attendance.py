from ..models import Attendance
from ..serializers import AttendanceSerializer
from .base import SessionScopedViewSet


class AttendanceViewSet(SessionScopedViewSet):
    serializer_class = AttendanceSerializer
    queryset = Attendance.objects.all()
