"""Role based permissions."""
from __future__ import annotations

from rest_framework.permissions import BasePermission

from common.enums import UserRole


class IsAdmin(BasePermission):
    """Allows access only to users with the ADMIN role."""

    message = "Admin privileges are required."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.role == UserRole.ADMIN)


class IsUser(BasePermission):
    message = "User privileges are required."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.role == UserRole.USER)


class IsOwner(BasePermission):
    """Object-level ownership check."""

    message = "You do not have permission to access this resource."

    def has_object_permission(self, request, view, obj) -> bool:
        owner = getattr(obj, "user", None)
        return owner is not None and owner == request.user
