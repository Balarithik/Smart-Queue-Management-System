from django.urls import path

from reports.views import OrganizationReportView, QueueReportView, UserReportView

urlpatterns = [
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
