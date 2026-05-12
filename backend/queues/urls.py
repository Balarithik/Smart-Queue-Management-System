from django.urls import path

from queues.views import (
    QueueCreateView,
    QueueDashboardView,
    QueueJoinView,
    QueueManageDetailView,
    QueueNextView,
    QueuePublicDetailView,
    QueueStatusView,
)

urlpatterns = [
    path("", QueueCreateView.as_view(), name="queue-create"),
    path("<uuid:public_id>/", QueuePublicDetailView.as_view(), name="queue-public-detail"),
    path("<uuid:public_id>/manage/", QueueManageDetailView.as_view(), name="queue-manage-detail"),
    path("<uuid:public_id>/join/", QueueJoinView.as_view(), name="queue-join"),
    path("<uuid:public_id>/status/", QueueStatusView.as_view(), name="queue-status"),
    path("<uuid:public_id>/next/", QueueNextView.as_view(), name="queue-next"),
    path("<uuid:public_id>/dashboard/", QueueDashboardView.as_view(), name="queue-dashboard"),
]
