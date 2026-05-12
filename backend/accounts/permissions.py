from rest_framework.permissions import BasePermission

from accounts.models import User


class HasRole(BasePermission):
    """Grant access only if the authenticated user has one of the allowed roles."""

    allowed_roles: tuple[str, ...] = ()

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        role = getattr(user, "role", User.Role.USER)
        return role in self.allowed_roles


class IsAdminRole(HasRole):
    allowed_roles = (User.Role.ADMIN,)


class IsOrganizationRole(HasRole):
    allowed_roles = (User.Role.ORGANIZATION, User.Role.ADMIN)


class IsUserRole(HasRole):
    allowed_roles = (User.Role.USER, User.Role.ORGANIZATION, User.Role.ADMIN)
