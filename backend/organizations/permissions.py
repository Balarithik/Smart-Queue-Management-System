from rest_framework.permissions import BasePermission

from accounts.models import User
from organizations.models import Organization


class IsOrganizationOwnerOrAdmin(BasePermission):
    """Allow ADMIN or the organization owner."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        role = getattr(user, "role", User.Role.USER)
        if role == User.Role.ADMIN:
            return True
        if isinstance(obj, Organization):
            return obj.owner_id == user.id
        # Queue from queues.models
        org = getattr(obj, "organization", None)
        if org is not None:
            return org.owner_id == user.id or role == User.Role.ADMIN
        return False
