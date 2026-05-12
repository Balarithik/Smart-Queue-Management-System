"""Helpers for issuing JWT pairs outside of the login view (e.g. registration)."""

from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User


def issue_tokens(user: User) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    refresh["role"] = user.role
    access = refresh.access_token
    access["role"] = user.role
    access["username"] = user.username
    return {"refresh": str(refresh), "access": str(access)}
