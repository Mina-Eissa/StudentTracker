from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from core.permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated
from core.models import AppUser


class GetAllOfUsersView(APIView):
    """GET /api/v1/users/  (Admin only)

    Returns a list of all users in the system, including their roles and
    basic profile information. Admin-only access.
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        headers = {
            "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
        }
        try:
            users = AppUser.objects.all()
            user_list = [
                {
                    "id": str(user.id),
                    "email": user.email,
                    "first_name": user.first_name,
                    "middle_name": user.middle_name,
                    "last_name": user.last_name,
                    "role": user.role,
                }
                for user in users
            ]
            return Response(user_list, status=200)
        except Exception as e:
            return Response({"detail": f"Failed to retrieve users: {e}"}, status=500)
