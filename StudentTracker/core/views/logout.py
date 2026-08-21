import requests
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.authentication import SupabaseAuthentication

from django.conf import settings


class LogoutView(APIView):
    """POST /api/auth/logout/  (private)

    Logs out the user by revoking the refresh token in Supabase Auth.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [SupabaseAuthentication]

    def post(self, request):
        token = request.auth  # Get the access token from the request's authentication
        if not token:
            return Response({"detail": "token is required."}, status=400)

        resp = requests.post(
            f"{settings.SUPABASE_URL}/auth/v1/logout",
            headers={
                "apikey": settings.SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        if resp.status_code >= 400:
            return Response({"detail": "Failed to log out."}, status=400)

        return Response({"detail": "Logged out successfully."}, status=200)
