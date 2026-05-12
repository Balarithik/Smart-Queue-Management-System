from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import (
    AdminPingView,
    LoginView,
    MeView,
    OrganizationPingView,
    RegisterView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="accounts-register"),
    path("token/", LoginView.as_view(), name="accounts-token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="accounts-token-refresh"),
    path("me/", MeView.as_view(), name="accounts-me"),
    path("admin/ping/", AdminPingView.as_view(), name="accounts-admin-ping"),
    path("organization/ping/", OrganizationPingView.as_view(), name="accounts-organization-ping"),
]
