from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdmin
from core.models import AppUser


class GetAllOfTeachersView(APIView):
    """GET /api/v1/teachers/  (Admin only)

    Returns a list of all teachers in the system, including their roles and
    basic profile information. Admin-only access.
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        try:
            teachers = AppUser.objects.filter(role="Teacher")
            teacher_list = [
                {
                    "id": str(teacher.id),
                    "email": teacher.email,
                    "first_name": teacher.first_name,
                    "middle_name": teacher.middle_name,
                    "last_name": teacher.last_name,
                    "role": teacher.role,
                }
                for teacher in teachers
            ]
            return Response(teacher_list, status=200)
        except Exception as e:
            return Response({"detail": f"Failed to retrieve teachers: {e}"}, status=500)
