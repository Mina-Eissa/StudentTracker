from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from ..models import BathroomLog
from ..serializers import BathroomLogSerializer
from .base import SessionScopedViewSet


class BathroomLogViewSet(SessionScopedViewSet):

    permission_classes = [IsAuthenticated]
    serializer_class = BathroomLogSerializer
    queryset = BathroomLog.objects.all()
    http_method_names = ["get", "head", "delete"]

    def destroy(self, request, *args, **kwargs):
        if request.user.role != "Admin":
            raise PermissionDenied(
                "Teachers cannot delete bathroom logs."
            )

        return super().destroy(request, *args, **kwargs)
