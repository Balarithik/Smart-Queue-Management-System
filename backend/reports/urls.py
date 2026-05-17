from django.urls import path

from reports.views import (
    OrganizationReportView,
    PlatformDashboardView,
    QueueReportView,
    UserReportView,
)

urlpatterns = [
    path("platform/", PlatformDashboardView.as_view(), name="report-platform"),
    path(
        "organizations/<int:pk>/",
        OrganizationReportView.as_view(),
        name="report-organization",
    ),
    path(
        "queues/<uuid:public_id>/",
        QueueReportView.as_view(),
        name="report-queue",
    ),
    path("users/", UserReportView.as_view(), name="report-users"),
]
