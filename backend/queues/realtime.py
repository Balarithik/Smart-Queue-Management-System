"""Queue status snapshots for HTTP polling and future WebSocket pushes."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db.models import Avg, DurationField, ExpressionWrapper, F
from django.utils import timezone

from queues.models import Queue, QueueEntry

RECENT_COMPLETED_LIMIT = 20
COMPLETED_LOOKBACK_DAYS = 7


class QueueUpdatePublisher:
    """Placeholder for Django Channels / ASGI broadcast."""

    @staticmethod
    def publish(queue_public_id: str, payload: dict[str, Any]) -> None:
        """No-op until WebSocket layer exists."""
        del queue_public_id, payload


def get_now_serving_token(queue: Queue) -> int | None:
    return (
        QueueEntry.objects.filter(queue=queue, status=QueueEntry.Status.CALLED)
        .order_by("-token")
        .values_list("token", flat=True)
        .first()
    )


def _avg_service_seconds(queue: Queue) -> float | None:
    recent = (
        QueueEntry.objects.filter(
            queue=queue,
            status=QueueEntry.Status.COMPLETED,
            completed_at__isnull=False,
        )
        .order_by("-completed_at")[:RECENT_COMPLETED_LIMIT]
    )
    durations = []
    for entry in recent:
        if entry.joined_at and entry.completed_at:
            durations.append((entry.completed_at - entry.joined_at).total_seconds())
    if durations:
        return sum(durations) / len(durations)

    cutoff = timezone.now() - timedelta(days=COMPLETED_LOOKBACK_DAYS)
    avg = (
        QueueEntry.objects.filter(
            queue=queue,
            status=QueueEntry.Status.COMPLETED,
            completed_at__gte=cutoff,
            completed_at__isnull=False,
        )
        .annotate(
            service=ExpressionWrapper(
                F("completed_at") - F("joined_at"),
                output_field=DurationField(),
            )
        )
        .aggregate(avg=Avg("service"))["avg"]
    )
    if avg is None:
        return None
    return avg.total_seconds()


def _waiting_ahead(queue: Queue, entry: QueueEntry) -> int:
    if entry.status != QueueEntry.Status.WAITING:
        return 0
    return QueueEntry.objects.filter(
        queue=queue,
        status=QueueEntry.Status.WAITING,
        token__lt=entry.token,
    ).count()


def _compute_eta_seconds(
    queue: Queue,
    entry: QueueEntry,
    waiting_ahead: int,
) -> int | None:
    if not queue.is_active:
        return None
    if entry.status in (QueueEntry.Status.CALLED, QueueEntry.Status.COMPLETED):
        return 0
    if entry.status != QueueEntry.Status.WAITING:
        return None
    avg = _avg_service_seconds(queue)
    if avg is None:
        return None
    return max(0, round(avg * (waiting_ahead + 1)))


def build_queue_status_snapshot(
    queue: Queue,
    entry: QueueEntry,
) -> dict[str, Any]:
    """Single source of truth for polling and future WebSocket payloads."""
    waiting_ahead = _waiting_ahead(queue, entry)
    if entry.status == QueueEntry.Status.WAITING:
        position = waiting_ahead + 1
    else:
        position = 0

    waiting_count = QueueEntry.objects.filter(
        queue=queue,
        status=QueueEntry.Status.WAITING,
    ).count()
    current_token = get_now_serving_token(queue)
    queue_status = "OPEN" if queue.is_active else "CLOSED"

    return {
        "public_id": str(queue.public_id),
        "queue_name": queue.name,
        "queue_status": queue_status,
        "is_active": queue.is_active,
        "current_token": current_token,
        "waiting_count": waiting_count,
        "token": entry.token,
        "status": entry.status,
        "position": position,
        "waiting_ahead": waiting_ahead,
        "eta_seconds": _compute_eta_seconds(queue, entry, waiting_ahead),
        "updated_at": timezone.now().isoformat(),
    }


def publish_queue_update(queue: Queue, entry: QueueEntry) -> None:
    """Broadcast snapshot after queue state changes (no-op until WebSockets)."""
    payload = build_queue_status_snapshot(queue, entry)
    QueueUpdatePublisher.publish(str(queue.public_id), payload)
