"""
High-level integration hooks for other apps (queues, etc.).

Call these from transactional code; queue-close uses ``transaction.on_commit``
in ``notifications.signals`` so side effects run only after a successful commit.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from notifications.services import (
    NotificationContext,
    NotificationEvent,
    get_notification_orchestrator,
)

if TYPE_CHECKING:
    from queues.models import Queue, QueueEntry


def notify_user_joined_queue(
    queue: Queue,
    entry: QueueEntry,
    *,
    waiting_ahead: int,
) -> None:
    """Fired when a customer receives a new queue token (join)."""
    ctx = NotificationContext(
        event=NotificationEvent.USER_JOINED_QUEUE,
        queue_public_id=str(queue.public_id),
        queue_name=queue.name,
        organization_id=queue.organization_id,
        token=entry.token,
        metadata={
            "waiting_ahead": waiting_ahead,
            "entry_id": entry.pk,
        },
    )
    get_notification_orchestrator().dispatch(ctx)


def notify_user_became_active(queue: Queue, entry: QueueEntry) -> None:
    """Fired when a waiting entry is called (token is now active / being served)."""
    ctx = NotificationContext(
        event=NotificationEvent.USER_BECAME_ACTIVE,
        queue_public_id=str(queue.public_id),
        queue_name=queue.name,
        organization_id=queue.organization_id,
        token=entry.token,
        metadata={"entry_id": entry.pk, "status": entry.status},
    )
    get_notification_orchestrator().dispatch(ctx)


def notify_queue_closed(queue: Queue, *, reason: str | None = None) -> None:
    """Fired when a queue stops accepting joins (``is_active`` becomes false)."""
    ctx = NotificationContext(
        event=NotificationEvent.QUEUE_CLOSED,
        queue_public_id=str(queue.public_id),
        queue_name=queue.name,
        organization_id=queue.organization_id,
        token=None,
        metadata={"reason": reason or "queue_deactivated"},
    )
    get_notification_orchestrator().dispatch(ctx)
