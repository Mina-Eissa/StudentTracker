from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from core.authentication import SupabaseAuthentication
from ..serializers import AppUserSerializer


class MeView(APIView):
    """GET /api/users/me/ — returns the profile of whoever the Bearer token belongs to."""
    authentication_classes = [SupabaseAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(AppUserSerializer(request.user).data)
