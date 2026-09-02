import jwt

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from jwt import PyJWKClient

from .models import AppUser


class SupabaseAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        if not auth_header.startswith(f"{self.keyword} "):
            return None

        token = auth_header.split(" ", 1)[1].strip()

        if not token:
            raise AuthenticationFailed("Empty bearer token.")

        try:
            jwks_client = PyJWKClient(
                settings.SUPABASE_JWKS_URL
            )

            signing_key = jwks_client.get_signing_key_from_jwt(token)

            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256"],
                audience="authenticated",
                issuer=f"{settings.SUPABASE_URL}/auth/v1",
            )

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired.")

        except jwt.InvalidAudienceError:
            raise AuthenticationFailed("Invalid token audience.")

        except jwt.InvalidIssuerError:
            raise AuthenticationFailed("Invalid token issuer.")

        except jwt.PyJWKError as e:
            raise AuthenticationFailed(f"Invalid signing key: {e}")

        except jwt.PyJWTError as e:
            raise AuthenticationFailed(f"Invalid token: {e}")

        user_id = payload.get("sub")

        if not user_id:
            raise AuthenticationFailed(
                "Token payload missing 'sub' claim."
            )

        try:
            user = AppUser.objects.get(id=user_id)
        except AppUser.DoesNotExist:
            raise AuthenticationFailed(
                "No matching AppUser for this token."
            )

        return (user, token)

    def authenticate_header(self, request):
        return self.keyword
