from django.urls import path

from organizations.views import (
    OrganizationCreateView,
    OrganizationMeView,
    OrganizationQueuesView,
    OrganizationStatsView,
)

urlpatterns = [
    path("", OrganizationCreateView.as_view(), name="organization-create"),
    path("me/", OrganizationMeView.as_view(), name="organization-me"),
    path("<int:pk>/queues/", OrganizationQueuesView.as_view(), name="organization-queues"),
    path("<int:pk>/stats/", OrganizationStatsView.as_view(), name="organization-stats"),
]
