from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Allows access only to users with role='Admin'."""

    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user, "role", None) == "Admin")


class IsAdminOrReadOnly(BasePermission):
    """Any authenticated user can read; only Admins can write."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return getattr(request.user, "role", None) == "Admin"
