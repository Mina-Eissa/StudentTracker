import requests
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import AppUser
from ..serializers import AppUserSerializer


class SignInView(APIView):
    """POST /api/auth/signin/  (public)
    Body: { email, password }

    Signs in against Supabase Auth on the frontend's behalf and returns the
    access token plus the caller's own profile in one response.
    """

    permission_classes = [AllowAny]
    # nothing to verify yet — that's the point of this endpoint
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response({"detail": "email and password are required."}, status=400)

        resp = requests.post(
            f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": settings.SUPABASE_ANON_KEY,
                     "Content-Type": "application/json"},
            json={"email": email, "password": password},
            timeout=10,
        )
        if resp.status_code >= 400:
            return Response({"detail": "Invalid email or password."}, status=401)

        data = resp.json()
        auth_user_id = data.get("user", {}).get("id")

        profile = AppUser.objects.filter(id=auth_user_id).first()
        if not profile:
            return Response(
                {
                    "detail": (
                        "Signed in with Supabase, but no matching profile exists yet. "
                        "Contact an admin."
                    )
                },
                status=403,
            )

        return Response(
            {
                "access_token": data.get("access_token"),
                "refresh_token": data.get("refresh_token"),
                "expires_in": data.get("expires_in"),
                "user": AppUserSerializer(profile).data,
            }
        )
