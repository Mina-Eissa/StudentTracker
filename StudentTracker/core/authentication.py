import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import AppUser


class SupabaseAuthentication(BaseAuthentication):
    """Verifies the Supabase-issued JWT the frontend sends as
    Authorization: Bearer <token>, then loads the matching AppUser.

    Does NOT touch Supabase over the network — the token is verified
    locally using the shared JWT secret, so this is fast and has no
    external dependency at request time.
    """

    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith(f"{self.keyword} "):
            return None  # no credentials supplied — let other auth classes / permissions decide

        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            raise AuthenticationFailed("Empty bearer token.")

        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",  # Supabase sets this audience on every user token
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired.")
        except jwt.PyJWTError as e:
            raise AuthenticationFailed(f"Invalid token: {e}")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationFailed("Token payload missing 'sub' claim.")

        try:
            user = AppUser.objects.get(id=user_id)
        except AppUser.DoesNotExist:
            # token is valid (they're a real Supabase auth user) but the
            # profiles-trigger row hasn't landed yet, or was deleted
            raise AuthenticationFailed("No matching AppUser for this token.")

        return (user, token)  # (request.user, request.auth)

    def authenticate_header(self, request):
        # returned in the 401 response's WWW-Authenticate header
        return self.keyword
