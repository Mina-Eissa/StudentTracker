import secrets

import requests
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import AppUser
from ..permissions import IsAdmin


class CreateUserView(APIView):
    """POST /api/users/create/  (Admin only)

    Creates a Supabase Auth account and the matching AppUser profile row.
    Admin-only creation is the whole point — there is no open signup path
    anywhere in this API.

    Two ways to hand the new user their credentials:

    1. Default (no "password" in the body): Supabase sends the new user
       an invite email with a link to set their own password. Nobody —
       including the admin — ever knows or handles that password.

    2. Fallback (admin supplies "password" in the body): used when email
       delivery isn't set up/reliable yet. The admin sets it directly and
       relays it to the user out of band; the user should change it after
       first login.
    """

    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        email = request.data.get("email")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        middle_name = request.data.get("middle_name", "")
        role = request.data.get("role")
        password = request.data.get("password")  # optional fallback

        if not all([email, first_name, last_name, role]):
            return Response(
                {"detail": "email, first_name, last_name, and role are required."}, status=400
            )
        if role not in ("Teacher", "Admin"):
            return Response({"detail": "role must be 'Teacher' or 'Admin'."}, status=400)
        if password and len(password) < 8:
            return Response({"detail": "password must be at least 8 characters."}, status=400)

        headers = {
            "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
        }

        if password:
            auth_user_id, error = self._create_with_password(
                email, password, headers)
        else:
            auth_user_id, error = self._create_with_invite(
                email, first_name, last_name, headers)

        if error:
            return error

        # create the matching profile row
        try:
            AppUser.objects.create(
                id=auth_user_id,
                first_name=first_name,
                middle_name=middle_name or None,
                last_name=last_name,
                email=email,
                role=role,
            )
        except Exception as e:
            # roll back the auth user so we don't leave an orphaned account
            requests.delete(
                f"{settings.SUPABASE_URL}/auth/v1/admin/users/{auth_user_id}",
                headers=headers,
                timeout=10,
            )
            return Response({"detail": f"Failed to create profile: {e}"}, status=500)

        response_body = {"id": auth_user_id, "email": email, "role": role}
        if password:
            response_body["note"] = (
                "Password set directly by admin — relay it to the user securely and "
                "have them change it after first login."
            )
        else:
            response_body["note"] = (
                "An invite email has been sent to the user with a link to set their "
                "own password. No one else knows or needs to handle it."
            )
        return Response(response_body, status=201)

    def _create_with_password(self, email, password, headers):
        """Admin-set-password path: creates the auth user directly, already confirmed."""
        resp = requests.post(
            f"{settings.SUPABASE_URL}/auth/v1/admin/users",
            headers=headers,
            json={"email": email, "password": password, "email_confirm": True},
            timeout=10,
        )
        if resp.status_code >= 400:
            return None, Response(
                {"detail": "Failed to create auth user.", "supabase_error": resp.json()}, status=400
            )
        return resp.json()["id"], None

    def _create_with_invite(self, email, first_name, last_name, headers):
        """Default path: creates the auth user unconfirmed and emails them an invite
        link to set their own password. Requires email sending to be configured on
        the Supabase project (it is, by default, within Supabase's rate limits)."""
        resp = requests.post(
            f"{settings.SUPABASE_URL}/auth/v1/invite",
            headers=headers,
            json={"email": email, "data": {
                "first_name": first_name, "last_name": last_name}},
            timeout=10,
        )
        if resp.status_code >= 400:
            return None, Response(
                {"detail": "Failed to send invite.", "supabase_error": resp.json()}, status=400
            )
        return resp.json()["id"], None
