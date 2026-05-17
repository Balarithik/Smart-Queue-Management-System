from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsOrganizationRole
from organizations.permissions import IsOrganizationOwnerOrAdmin
from queues.models import Queue, QueueEntry
from queues.pagination import QueueSearchPagination
from queues.realtime import build_queue_status_snapshot, publish_queue_update
from queues.serializers import (
    QueueCreateSerializer,
    QueuePublicSerializer,
    QueueSearchSerializer,
    QueueStaffSerializer,
    QueueStatusSnapshotSerializer,
)
from queues.services import join_queue


class QueueCreateView(generics.CreateAPIView):
    """POST /api/queues/ — create queue (ORGANIZATION / ADMIN)."""

    permission_classes = [IsAuthenticated, IsOrganizationRole]
    serializer_class = QueueCreateSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        queue = serializer.save()
        return Response(
            QueueStaffSerializer(queue, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class QueueSearchView(generics.ListAPIView):
    """GET /api/queues/search/?q=&page=&page_size=&is_active="""

    permission_classes = [AllowAny]
    serializer_class = QueueSearchSerializer
    pagination_class = QueueSearchPagination

    def get_queryset(self):
        qs = (
            Queue.objects.select_related("organization")
            .annotate(
                waiting_count=Count(
                    "entries",
                    filter=Q(entries__status=QueueEntry.Status.WAITING),
                )
            )
            .order_by("organization__name", "name")
        )

        is_active = self.request.query_params.get("is_active", "true")
        if is_active.lower() in ("1", "true", "yes"):
            qs = qs.filter(is_active=True)
        elif is_active.lower() in ("0", "false", "no"):
            qs = qs.filter(is_active=False)

        query = (self.request.query_params.get("q") or "").strip()
        if query:
            qs = qs.filter(
                Q(name__icontains=query) | Q(organization__name__icontains=query)
            )
        return qs


class QueuePublicDetailView(generics.RetrieveAPIView):
    """GET /api/queues/<public_id>/ — minimal metadata for join page."""

    permission_classes = [AllowAny]
    queryset = Queue.objects.all()
    serializer_class = QueuePublicSerializer
    lookup_field = "public_id"


class QueueManageDetailView(generics.RetrieveAPIView):
    """GET /api/queues/<public_id>/manage/ — staff detail + QR."""

    permission_classes = [IsAuthenticated, IsOrganizationOwnerOrAdmin]
    queryset = Queue.objects.select_related("organization")
    serializer_class = QueueStaffSerializer
    lookup_field = "public_id"


class QueueJoinView(APIView):
    """POST /api/queues/<public_id>/join/ — take a number (public)."""

    permission_classes = [AllowAny]

    def post(self, request, public_id):
        try:
            payload = join_queue(public_id)
        except Queue.DoesNotExist:
            return Response({"detail": "Queue not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(payload, status=status.HTTP_201_CREATED)


class QueueStatusView(APIView):
    """GET /api/queues/<public_id>/status/?token= — entry status (public)."""

    permission_classes = [AllowAny]

    def get(self, request, public_id):
        raw = request.query_params.get("token")
        if raw is None:
            return Response(
                {"detail": "Query parameter 'token' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = int(raw)
        except ValueError:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        queue = get_object_or_404(Queue, public_id=public_id)
        entry = get_object_or_404(QueueEntry, queue=queue, token=token)
        data = build_queue_status_snapshot(queue, entry)
        serializer = QueueStatusSnapshotSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class QueueNextView(APIView):
    """POST /api/queues/<public_id>/next/ — call next waiting token (staff)."""

    permission_classes = [IsAuthenticated, IsOrganizationOwnerOrAdmin]

    def post(self, request, public_id):
        queue = get_object_or_404(Queue.objects.select_related("organization"), public_id=public_id)
        self.check_object_permissions(request, queue)

        now = timezone.now()
        with transaction.atomic():
            Queue.objects.select_for_update().get(pk=queue.pk)
            current_called = (
                QueueEntry.objects.select_for_update()
                .filter(queue=queue, status=QueueEntry.Status.CALLED)
                .order_by("token")
                .first()
            )
            if current_called is not None:
                current_called.status = QueueEntry.Status.COMPLETED
                current_called.completed_at = now
                current_called.save(update_fields=["status", "completed_at"])

            entry = (
                QueueEntry.objects.select_for_update()
                .filter(queue=queue, status=QueueEntry.Status.WAITING)
                .order_by("token")
                .first()
            )
            if entry is None:
                remaining = QueueEntry.objects.filter(
                    queue=queue, status=QueueEntry.Status.WAITING
                ).count()
                return Response(
                    {
                        "called_token": None,
                        "remaining_waiting": remaining,
                        "detail": "No waiting entries.",
                    }
                )
            entry.status = QueueEntry.Status.CALLED
            entry.called_at = now
            entry.save(update_fields=["status", "called_at"])
            remaining = QueueEntry.objects.filter(
                queue=queue, status=QueueEntry.Status.WAITING
            ).count()

        from notifications.hooks import notify_user_became_active

        notify_user_became_active(queue, entry)

        def _publish() -> None:
            publish_queue_update(queue, entry)

        transaction.on_commit(_publish)

        return Response(
            {
                "called_token": entry.token,
                "remaining_waiting": remaining,
            }
        )


class QueueDashboardView(APIView):
    """GET /api/queues/<public_id>/dashboard/ — operator dashboard."""

    permission_classes = [IsAuthenticated, IsOrganizationOwnerOrAdmin]

    def get(self, request, public_id):
        queue = get_object_or_404(
            Queue.objects.select_related("organization"),
            public_id=public_id,
        )
        self.check_object_permissions(request, queue)

        waiting_qs = QueueEntry.objects.filter(queue=queue, status=QueueEntry.Status.WAITING)
        waiting_count = waiting_qs.count()
        now_serving = (
            QueueEntry.objects.filter(queue=queue, status=QueueEntry.Status.CALLED)
            .order_by("-token")
            .values_list("token", flat=True)
            .first()
        )
        latest_waiting_tokens = list(
            waiting_qs.order_by("-token").values_list("token", flat=True)[:10]
        )

        return Response(
            {
                "queue": QueueStaffSerializer(queue, context={"request": request}).data,
                "waiting_count": waiting_count,
                "now_serving_token": now_serving,
                "latest_waiting_tokens": latest_waiting_tokens,
            }
        )
